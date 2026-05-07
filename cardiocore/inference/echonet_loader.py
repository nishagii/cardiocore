# OWNER: Teammate A
# DAY:   3 (after EchoNet data use agreement is approved)
# PURPOSE: Load EchoNet pretrained weights and run EF regression
#
# EchoNet-Dynamic: github.com/echonet/dynamic
# Trained on 10,030 echocardiogram videos from Stanford Medicine
# Published MAE: ~4% on ejection fraction estimation
#
# Data use agreement: echonet.github.io/dynamic
# Submit the form on Day 1. Approval takes 1-3 days.
#
# Once weights are downloaded to models/echonet/, implement predict_ef().
# inference/echo.py will automatically use it via try/import.

def predict_ef(video_path: str) -> float:
    """
    Run EchoNet model on a video file and return EF percentage (0-100).
    Raises ImportError if weights are not yet downloaded.
    inference/echo.py catches this and falls back to Gemma 4 estimation.
    """
    raise ImportError(
        "EchoNet weights not yet loaded. "
        "Waiting for data use agreement approval at echonet.github.io/dynamic. "
        "inference/echo.py will use Gemma 4 visual estimation as fallback."
    )
