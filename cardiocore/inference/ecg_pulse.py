"""
PULSE-7B inference for ECG images.
Loaded once at specialist server startup, kept in GPU memory.
"""
import io
import json
import os
from typing import Optional

import torch
from PIL import Image

from inference.config import ECG_CLASSES, ECG_SNOMED


_MODEL = None
_PROCESSOR = None

# PULSE-7B is a LLaVA-architecture VLM. Verify exact class against the
# model card README before deployment if it has been updated.
_MODEL_ID = os.getenv('PULSE_MODEL_ID', 'PULSE-ECG/PULSE-7B')


ECG_PROMPT = """You are a clinical cardiologist analyzing a 12-lead ECG image.

Classify the rhythm into exactly one of:
- NORM (normal sinus rhythm)
- MI (myocardial infarction)
- STTC (ST-T wave change)
- CD (conduction disorder)
- HYP (cardiac hypertrophy)

Respond with valid JSON only, no other text:
{
  "rhythm_class": "NORM|MI|STTC|CD|HYP",
  "confidence": <number between 0 and 1>,
  "clinical_flags": ["list specific findings, max 4"],
  "reasoning": "one sentence explanation"
}"""


def _load_model():
    """Load PULSE-7B using native LLaVA runtime."""

    global _MODEL, _PROCESSOR

    if _MODEL is not None:
        return _MODEL, _PROCESSOR

    print(f'Loading {_MODEL_ID} with LLaVA runtime...')

    from llava.model.builder import load_pretrained_model
    from llava.mm_utils import get_model_name_from_path

    model_name = get_model_name_from_path(_MODEL_ID)

    tokenizer, model, image_processor, context_len = \
        load_pretrained_model(
            model_path=_MODEL_ID,
            model_base=None,
            model_name=model_name,
            device="cuda",
        )

    _MODEL = model
    _PROCESSOR = {
        "tokenizer": tokenizer,
        "image_processor": image_processor,
        "context_len": context_len,
    }

    print(
        f'PULSE-7B ready. GPU: '
        f'{torch.cuda.memory_allocated()/1e9:.2f}GB'
    )

    return _MODEL, _PROCESSOR


def _extract_json(text: str) -> dict:
    """Find and parse JSON block in PULSE-7B's response."""
    text = text.strip()
    if '```' in text:
        for part in text.split('```'):
            part = part.strip().lstrip('json').strip()
            try:
                return json.loads(part)
            except Exception:
                continue
    # Fallback: find first { ... } block
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except Exception:
            pass
    return {}


def analyze_ecg_image(image_bytes: bytes) -> dict:
    """Run PULSE-7B on an ECG image. Return the structured result."""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    try:
        model, processor = _load_model()

        # LLaVA-1.5 chat template
        conversation = [
            {
                'role': 'user',
                'content': [
                    {'type': 'image'},
                    {'type': 'text', 'text': ECG_PROMPT},
                ],
            },
        ]
        prompt = processor.apply_chat_template(
            conversation, add_generation_prompt=True
        )

        inputs = processor(
            images=img, text=prompt, return_tensors='pt'
        ).to(model.device, torch.float16)

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
            )

        # Decode only the new tokens (skip the prompt echo)
        input_len = inputs['input_ids'].shape[1]
        decoded = processor.decode(out[0][input_len:], skip_special_tokens=True)
        result = _extract_json(decoded)

    except Exception as e:
        print(f'PULSE-7B inference failed: {e}')
        result = {}

    cls = result.get('rhythm_class', 'NORM').upper().strip()
    if cls not in ECG_CLASSES:
        cls = 'NORM'

    try:
        confidence = float(result.get('confidence', 0.5))
        confidence = max(0.0, min(1.0, confidence))
    except (TypeError, ValueError):
        confidence = 0.5

    clinical_flags = result.get('clinical_flags', [])
    if not isinstance(clinical_flags, list):
        clinical_flags = [str(clinical_flags)]

    snomed_code, snomed_desc = ECG_SNOMED.get(cls, ECG_SNOMED['NORM'])
    return {
        'rhythm_class':       cls,
        'confidence':         confidence,
        'all_class_probs':    {c: 0.0 for c in ECG_CLASSES},  # PULSE doesn't natively output per-class probs
        'snomed_code':        snomed_code,
        'snomed_description': snomed_desc,
        'clinical_flags':     clinical_flags[:4],
        'reasoning':          str(result.get('reasoning', f'Classified as {cls}')),
    }