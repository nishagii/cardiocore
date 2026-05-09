import base64, io, json
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

def analyze_echo(video_path: str) -> dict:
    frames = extract_frames(video_path, n=8)

    # Try EchoNet if weights available
    ef_from_echonet = None
    try:
        from inference.echonet_loader import predict_ef
        ef_from_echonet = predict_ef(video_path)
    except ImportError:
        pass  # EchoNet not set up yet — use Gemma 4 fallback

    if ef_from_echonet is not None:
        prompt = f'EchoNet model predicted EF={ef_from_echonet:.1f}%. Confirm and provide assessment:' + ECHO_EF_PROMPT.split('{n}')[1]
        prompt = prompt.format(n=len(frames))
    else:
        prompt = ECHO_EF_PROMPT.format(n=len(frames))

    try:
        raw    = get_client().chat(ECHO_EF_SYSTEM, prompt, frames)
        result = get_client().parse_json(raw)
    except Exception:
        result = {'ef_percent': ef_from_echonet or 55.0,
                  'hf_classification':'Normal','wall_motion_flags':[],
                  'confidence':0.5,'reasoning':'Analysis unavailable'}

    ef  = max(0.0, min(100.0, float(result.get('ef_percent', 55.0))))
    hfc = result.get('hf_classification', classify_hf(ef))
    if hfc not in HF_CLASSES: hfc = classify_hf(ef)
    code, desc, _, _ = HF_CLASSES[hfc]
    return {
        'ef_percent':            ef,
        'ef_source':             'echonet' if ef_from_echonet else 'gemma4',
        'hf_classification':     hfc,
        'hf_snomed_code':        code,
        'hf_snomed_description': desc,
        'wall_motion_flags':     result.get('wall_motion_flags', []),
        'confidence':            float(result.get('confidence', 0.8)),
        'reasoning':             result.get('reasoning', ''),
    }

def classify_hf(ef):
    if ef < 40: return 'HFrEF'
    if ef < 50: return 'HFmrEF'
    if ef < 55: return 'Borderline'
    return 'Normal'

