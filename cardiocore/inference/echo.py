# OWNER: Binula
# DAY:   2
# PURPOSE: Echo EF estimation using EchoNet model + Gemma 4 interpretation
#
# Uses: EchoNet-Dynamic pretrained model (Stanford, MAE ~4%)
#       Gemma 4 for interpretation and fallback EF estimation
#
# Expected interface (do not change function names):
#
#   from inference.echo import analyze_echo
#
#   result = analyze_echo("path/to/video.avi")
#   # returns: {ef_percent, ef_source, hf_classification, hf_snomed_code,
#   #           hf_snomed_description, wall_motion_flags, confidence, reasoning}

"""
Echocardiogram analysis: LV ejection fraction estimation.

Uses EchoNet-Dynamic if weights are available; falls back to Gemma 4
multimodal as the vision-language judge otherwise.
"""
import base64
import io
import json
from typing import Optional

import numpy as np
from PIL import Image

from inference.config import HF_CLASSES
from inference.gemma4_client import get_client
from inference.echo_structure import extract_frames


ECHO_EF_SYSTEM = 'You are a cardiac imaging specialist. Respond with valid JSON only.'

ECHO_EF_PROMPT = '''These {n} frames are from an apical 4-chamber echocardiogram.
Estimate the left ventricular ejection fraction.
Compare LV size at end-diastole vs end-systole.
{{
  "ef_percent": <0-100>,
  "hf_classification": "HFrEF|HFmrEF|Borderline|Normal",
  "wall_motion_flags": ["list"],
  "confidence": <0-1>,
  "reasoning": "one sentence"
}}
EF guide: <40=HFrEF, 40-49=HFmrEF, 50-54=Borderline, >=55=Normal'''


def _build_confirm_prompt(ef_value: float, n_frames: int) -> str:
    """Prompt used when EchoNet has produced an EF estimate already."""
    return (
        f'EchoNet predicted EF={ef_value:.1f}% from these {n_frames} '
        f'apical 4-chamber frames. Confirm and provide assessment.\n\n'
        f'Compare LV size at end-diastole vs end-systole.\n'
        '{\n'
        '  "ef_percent": <0-100>,\n'
        '  "hf_classification": "HFrEF|HFmrEF|Borderline|Normal",\n'
        '  "wall_motion_flags": ["list"],\n'
        '  "confidence": <0-1>,\n'
        '  "reasoning": "one sentence"\n'
        '}\n'
        'EF guide: <40=HFrEF, 40-49=HFmrEF, 50-54=Borderline, >=55=Normal'
    )


def _try_echonet(video_path: str) -> Optional[float]:
    """
    Attempt EchoNet inference. Return EF percent on success, None on any
    failure (missing weights, runtime error, unreadable video).
    """
    try:
        from inference.echonet_loader import predict_ef
    except ImportError:
        # Module not present or weights not configured.
        return None

    try:
        return predict_ef(video_path)
    except ImportError:
        # echonet_loader raises ImportError specifically when weights
        # are missing at runtime; treat as a clean fallback.
        return None
    except Exception as e:
        # Any other failure: log and fall back gracefully.
        print(f'EchoNet inference failed, falling back to Gemma 4: {e}')
        return None


def _safe_chat_and_parse(system: str, prompt: str, frames: list) -> dict:
    """
    Call the multimodal client and parse JSON. On any failure, return an
    empty dict so the caller can apply defaults consistently.
    """
    try:
        client = get_client()
        raw = client.chat(system, prompt, frames)
        parsed = client.parse_json(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception as e:
        print(f'Gemma 4 echo analysis failed: {e}')
        return {}


def analyze_echo(video_path: str) -> dict:
    """
    Analyse an echocardiogram video and return a structured EF assessment.

    Pipeline:
      1. Extract sampled frames.
      2. Try EchoNet for a numeric EF estimate.
      3. Send frames + (optional EchoNet prior) to Gemma 4 for assessment.
      4. Reconcile, classify HF, attach SNOMED codes.

    Always returns a well-formed dict, even when every model fails.
    """
    # Step 1: extract frames. If this fails, we cannot proceed at all.
    try:
        frames = extract_frames(video_path, n=2)
    except Exception as e:
        print(f'Frame extraction failed for {video_path}: {e}')
        return _default_result(
            ef=55.0,
            source='unavailable',
            reasoning=f'Frame extraction failed: {e}',
            confidence=0.0,
        )

    if not frames:
        return _default_result(
            ef=55.0,
            source='unavailable',
            reasoning='No frames extracted from video.',
            confidence=0.0,
        )

    # Step 2: try EchoNet first.
    ef_from_echonet = _try_echonet(video_path)

    # Step 3: build the right prompt and call Gemma 4.
    if ef_from_echonet is not None:
        prompt = _build_confirm_prompt(ef_from_echonet, len(frames))
    else:
        prompt = ECHO_EF_PROMPT.format(n=len(frames))

    result = _safe_chat_and_parse(ECHO_EF_SYSTEM, prompt, frames)

    # Step 4: reconcile values, applying defaults where the model failed
    # or produced malformed output.
    if not result:
        # Gemma 4 failed entirely. Trust EchoNet if we have it.
        return _default_result(
            ef=ef_from_echonet if ef_from_echonet is not None else 55.0,
            source='echonet' if ef_from_echonet is not None else 'unavailable',
            reasoning='Vision-language analysis unavailable.',
            confidence=0.5 if ef_from_echonet is not None else 0.0,
        )

    # Pull EF, with EchoNet as the preferred fallback if Gemma 4 omitted it.
    raw_ef = result.get('ef_percent')
    if raw_ef is None:
        raw_ef = ef_from_echonet if ef_from_echonet is not None else 55.0

    try:
        ef = max(0.0, min(100.0, float(raw_ef)))
    except (TypeError, ValueError):
        ef = ef_from_echonet if ef_from_echonet is not None else 55.0
        ef = max(0.0, min(100.0, float(ef)))

    # HF classification: use the model's answer if it is a known label,
    # otherwise compute from EF directly.
    hfc = result.get('hf_classification')
    if hfc not in HF_CLASSES:
        hfc = classify_hf(ef)

    code, desc, _, _ = HF_CLASSES[hfc]

    # Confidence: clamp to [0, 1] in case the model emits something odd.
    try:
        confidence = float(result.get('confidence', 0.8))
    except (TypeError, ValueError):
        confidence = 0.8
    confidence = max(0.0, min(1.0, confidence))

    wall_motion = result.get('wall_motion_flags', [])
    if not isinstance(wall_motion, list):
        wall_motion = [str(wall_motion)]

    return {
        'ef_percent':            ef,
        'ef_source':             'echonet' if ef_from_echonet is not None else 'gemma4',
        'hf_classification':     hfc,
        'hf_snomed_code':        code,
        'hf_snomed_description': desc,
        'wall_motion_flags':     wall_motion,
        'confidence':            confidence,
        'reasoning':             str(result.get('reasoning', '')),
    }


def _default_result(ef: float, source: str, reasoning: str, confidence: float) -> dict:
    """Build a well-formed result when partial or full analysis fails."""
    ef = max(0.0, min(100.0, float(ef)))
    hfc = classify_hf(ef)
    code, desc, _, _ = HF_CLASSES[hfc]
    return {
        'ef_percent':            ef,
        'ef_source':             source,
        'hf_classification':     hfc,
        'hf_snomed_code':        code,
        'hf_snomed_description': desc,
        'wall_motion_flags':     [],
        'confidence':            max(0.0, min(1.0, float(confidence))),
        'reasoning':             reasoning,
    }


def classify_hf(ef: float) -> str:
    """Map an EF percentage to its heart-failure class."""
    if ef < 40:
        return 'HFrEF'
    if ef < 50:
        return 'HFmrEF'
    if ef < 55:
        return 'Borderline'
    return 'Normal'


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python -m inference.echo <path-to-echo.avi>')
        sys.exit(1)
    out = analyze_echo(sys.argv[1])
    print(json.dumps(out, indent=2))