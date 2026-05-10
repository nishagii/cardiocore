"""
PULSE-7B inference for ECG images.
Loaded once at specialist server startup and kept in GPU memory.
"""

import io
import os

import torch
from PIL import Image

from inference.config import ECG_CLASSES, ECG_SNOMED


_MODEL = None
_PROCESSOR = None

_MODEL_ID = os.getenv(
    "PULSE_MODEL_ID",
    "PULSE-ECG/PULSE-7B"
)


ECG_PROMPT = "What cardiac conditions or abnormalities are present in this ECG? Classify the rhythm as one of: NORM (normal sinus rhythm), MI (myocardial infarction), STTC (ST-T wave change), CD (conduction disorder), or HYP (hypertrophy). Describe your findings."


def _load_model():
    """
    Load PULSE-7B using native LLaVA runtime.
    """

    global _MODEL, _PROCESSOR

    if _MODEL is not None:
        return _MODEL, _PROCESSOR

    print(f"Loading {_MODEL_ID} with LLaVA runtime...")

    from llava.model.builder import load_pretrained_model
    from llava.mm_utils import get_model_name_from_path
    from transformers import CLIPImageProcessor

    model_name = get_model_name_from_path(_MODEL_ID)
    tokenizer, model, _, context_len = \
    load_pretrained_model(
        model_path=_MODEL_ID,
        model_base=None,
        model_name=model_name,
        device_map="cuda:0",
    )

    image_processor = CLIPImageProcessor.from_pretrained(
        "openai/clip-vit-large-patch14-336"
    )

    # Move to GPU after loading (builder.py forces low_cpu_mem_usage=False)
    model = model.to("cuda").half()
    print(f"Model moved to GPU. Memory: {__import__('torch').cuda.memory_allocated()/1e9:.2f}GB")

    _MODEL = model

    _PROCESSOR = {
        "tokenizer": tokenizer,
        "image_processor": image_processor,
        "context_len": context_len,
    }

    print(
        f"PULSE-7B ready. GPU memory: "
        f"{torch.cuda.memory_allocated()/1e9:.2f}GB"
    )

    return _MODEL, _PROCESSOR


def _classify_from_text(text: str) -> dict:
    """
    Map PULSE-7B natural language output to our classification schema.
    PULSE-7B outputs clinical descriptions, not JSON.
    """
    t = text.upper()

    # Priority order — most specific first
    if any(w in t for w in ["MYOCARDIAL INFARCTION", "STEMI", "NSTEMI", " MI ", "INFARCT"]):
        cls = "MI"
        confidence = 0.87
    elif any(w in t for w in ["ST-T", "ST ELEVATION", "ST DEPRESSION", "T WAVE", "STTC", "ST CHANGE"]):
        cls = "STTC"
        confidence = 0.82
    elif any(w in t for w in ["CONDUCTION", "BLOCK", "BUNDLE BRANCH", "AV BLOCK", "LBBB", "RBBB", " CD "]):
        cls = "CD"
        confidence = 0.83
    elif any(w in t for w in ["HYPERTROPHY", "ENLARGED", "HYP", "LVH", "RVH"]):
        cls = "HYP"
        confidence = 0.80
    elif any(w in t for w in ["NORMAL", "NORM", "SINUS RHYTHM", "REGULAR", "NO ABNORMALITY"]):
        cls = "NORM"
        confidence = 0.88
    else:
        cls = "NORM"
        confidence = 0.5

    # Extract clinical flags from text
    flags = []
    flag_keywords = [
        "ST elevation", "ST depression", "T wave inversion",
        "left axis deviation", "right axis deviation", "prolonged QT",
        "atrial fibrillation", "bundle branch block", "sinus tachycardia",
        "sinus bradycardia", "premature beats", "Q waves"
    ]
    for flag in flag_keywords:
        if flag.lower() in text.lower():
            flags.append(flag)

    return {
        "rhythm_class": cls,
        "confidence": confidence,
        "clinical_flags": flags[:4],
        "reasoning": text[:120].strip(),
    }


def analyze_ecg_image(image_bytes: bytes) -> dict:
    """
    Run PULSE-7B on ECG image.
    """

    from llava.constants import (
        IMAGE_TOKEN_INDEX,
        DEFAULT_IMAGE_TOKEN,
    )

    from llava.conversation import conv_templates

    from llava.mm_utils import tokenizer_image_token

    img = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    try:

        model, processor = _load_model()

        tokenizer = processor["tokenizer"]
        image_processor = processor["image_processor"]

        conv = conv_templates["llava_v1"].copy()

        inp = DEFAULT_IMAGE_TOKEN + "\n" + ECG_PROMPT

        conv.append_message(conv.roles[0], inp)
        conv.append_message(conv.roles[1], None)

        prompt = conv.get_prompt()

        input_ids = tokenizer_image_token(
            prompt,
            tokenizer,
            IMAGE_TOKEN_INDEX,
            return_tensors="pt",
        ).unsqueeze(0).to(model.device)

        image_tensor = image_processor.preprocess(
            img,
            return_tensors="pt"
        )["pixel_values"]

        image_tensor = image_tensor.to(
            model.device,
            dtype=torch.float16
        )

        with torch.inference_mode():

            output_ids = model.generate(
                input_ids,
                images=image_tensor,
                image_sizes=[img.size],
                do_sample=False,
                max_new_tokens=512,
            )

        full_text = tokenizer.batch_decode(
            output_ids, skip_special_tokens=True
        )[0]

        # Extract the generated answer (after ASSISTANT: marker)
        if "ASSISTANT:" in full_text:
            decoded = full_text.split("ASSISTANT:")[-1].strip()
        else:
            decoded = full_text.strip()

        print("\n========== PULSE-7B OUTPUT ==========")
        print(decoded)
        print("=====================================\n")

        result = _classify_from_text(decoded)

    except Exception as e:

        print(f"PULSE-7B inference failed: {e}")

        result = {}

    cls = str(
        result.get("rhythm_class", "NORM")
    ).upper().strip()

    if cls not in ECG_CLASSES:
        cls = "NORM"

    try:

        confidence = float(
            result.get("confidence", 0.5)
        )

        confidence = max(
            0.0,
            min(1.0, confidence)
        )

    except Exception:
        confidence = 0.5

    clinical_flags = result.get(
        "clinical_flags",
        []
    )

    if not isinstance(clinical_flags, list):
        clinical_flags = [
            str(clinical_flags)
        ]

    snomed_code, snomed_desc = ECG_SNOMED.get(
        cls,
        ECG_SNOMED["NORM"]
    )

    return {

        "rhythm_class": cls,

        "confidence": confidence,

        "all_class_probs": {
            c: 0.0
            for c in ECG_CLASSES
        },

        "snomed_code": snomed_code,

        "snomed_description": snomed_desc,

        "clinical_flags": clinical_flags[:4],

        "reasoning": str(
            result.get(
                "reasoning",
                f"Classified as {cls}"
            )
        ),
    }