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

# TODO: Binula implements this on Day 2
# See implementation guide for full code

def analyze_echo(video_path: str) -> dict:
    raise NotImplementedError("Binula: implement inference/echo.py on Day 2")
