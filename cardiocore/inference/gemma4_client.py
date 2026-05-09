import os

class StubClient:
    """Fake Gemma 4 client for local development. Returns canned JSON."""

    def chat(self, system, user_text, images_b64=None, max_tokens=400):
        # Return appropriate canned JSON based on prompt content
        prompt_lower = user_text.lower()
        if 'ejection fraction' in prompt_lower or 'ef_percent' in prompt_lower:
            return ('{"ef_percent": 55, "hf_classification": "Normal", '
                    '"wall_motion_flags": [], "confidence": 0.85, '
                    '"reasoning": "stub: normal LV systolic function"}')
        if 'lv_size' in prompt_lower or 'cardiac structure' in prompt_lower:
            return ('{"lv_size": "normal", "wall_thickness": "normal", '
                    '"structural_flags": [], "pericardial_effusion": false, '
                    '"confidence": 0.85, "reasoning": "stub: no structural abnormalities"}')
        if 'rhythm_class' in prompt_lower or 'ecg' in prompt_lower:
            return ('{"rhythm_class": "NORM", "confidence": 0.91, '
                    '"clinical_flags": [], "reasoning": "stub: normal sinus rhythm"}')
        return '{}'

    def parse_json(self, text):
        import json
        return json.loads(text.strip())

    def healthy(self):
        return True

    @property
    def model_id(self):
        return 'stub-gemma-4-12b'

    @property
    def base_url(self):
        return 'stub://local'


_client = None
def get_client():
    global _client
    if _client is None:
        if os.getenv('STUB_GEMMA') == '1':
            _client = StubClient()
        else:
            _client = Gemma4Client()
    return _client