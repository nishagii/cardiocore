import base64, io, json
import numpy as np
from PIL import Image
from inference.gemma4_client import get_client

ECHO_STRUCT_SYSTEM = 'You are a cardiac imaging specialist. Respond with valid JSON only.'
ECHO_STRUCT_PROMPT = '''These {n} echocardiogram frames show the cardiac structure.
Assess the following and respond with JSON:
{{
  "lv_size": "normal|dilated|hypertrophied",
  "wall_thickness": "normal|increased|decreased",
  "structural_flags": ["list observations"],
  "pericardial_effusion": false,
  "confidence": 0.0,
  "reasoning": "one sentence"
}}'''

def extract_frames(video_path: str, n: int = 2) -> list:
    import imageio
    reader = imageio.get_reader(video_path)
    total  = reader.count_frames()
    idxs   = np.linspace(0, total-1, min(n, total), dtype=int)
    frames = []
    for i in idxs:
        frame = reader.get_data(int(i))
        img   = Image.fromarray(frame).convert('L').resize((224,224))
        buf   = io.BytesIO()
        img.save(buf, format='PNG')
        frames.append(base64.b64encode(buf.getvalue()).decode())
    reader.close()
    return frames

def analyze_structure(video_path: str) -> dict:
    frames = extract_frames(video_path)
    prompt = ECHO_STRUCT_PROMPT.format(n=len(frames))
    try:
        raw = get_client().chat(ECHO_STRUCT_SYSTEM, prompt, frames)
        result = get_client().parse_json(raw)
    except Exception as e:
        result = {
            'lv_size': 'normal',
            'wall_thickness': 'normal',
            'structural_flags': [],
            'pericardial_effusion': False,
            'confidence': 0.5,
            'reasoning': f'Analysis unavailable: {str(e)}',
        }
    return result

