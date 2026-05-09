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

# cardiocore/inference/echonet_loader.py
"""
EchoNet-Dynamic loader for LV ejection fraction estimation.

Returns None on any failure so echo.py can fall back to Gemma 4.
Lazy-loads weights on first call to keep import cost low.
"""
import os
from pathlib import Path
from typing import Optional

import numpy as np
import torch

_MODEL = None
_DEVICE = None
_WEIGHTS_PATH = os.environ.get(
    "ECHONET_WEIGHTS",
    str(Path(__file__).parent.parent / "weights" / "echonet_dynamic.pt"),
)


def _load_model() -> Optional[torch.nn.Module]:
    """Load EchoNet-Dynamic weights once. Return None if unavailable."""
    global _MODEL, _DEVICE
    if _MODEL is not None:
        return _MODEL

    if not Path(_WEIGHTS_PATH).exists():
        # Weights not downloaded — caller will fall back to Gemma 4
        raise ImportError(f"EchoNet weights not found at {_WEIGHTS_PATH}")

    try:
        # EchoNet-Dynamic uses torchvision r2plus1d_18 with 1-channel input
        # and a single regression output (EF percent).
        import torchvision
        model = torchvision.models.video.r2plus1d_18(weights=None)
        # Replace first conv to accept grayscale (1 channel) input
        model.stem[0] = torch.nn.Conv3d(
            1, 64,
            kernel_size=(1, 7, 7),
            stride=(1, 2, 2),
            padding=(0, 3, 3),
            bias=False,
        )
        # Replace final fc to output a single scalar (EF)
        model.fc = torch.nn.Linear(model.fc.in_features, 1)

        state = torch.load(_WEIGHTS_PATH, map_location="cpu")
        # Some checkpoints wrap weights in {"state_dict": ...}
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        # Strip "module." prefix if saved from DataParallel
        state = {k.replace("module.", ""): v for k, v in state.items()}
        model.load_state_dict(state, strict=False)

        _DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(_DEVICE).eval()
        _MODEL = model
        return _MODEL
    except Exception as e:
        raise ImportError(f"Failed to initialise EchoNet: {e}") from e


def _load_clip(video_path: str, length: int = 32, size: int = 112) -> torch.Tensor:
    """
    Load a video clip as (1, 1, T, H, W) tensor of grayscale frames in [0, 1].
    """
    import imageio.v2 as imageio

    reader = imageio.get_reader(video_path)
    total = reader.count_frames()

    # Sample `length` evenly spaced frames
    if total >= length:
        idxs = np.linspace(0, total - 1, length, dtype=int)
    else:
        # Loop short clips to fill the window
        idxs = np.arange(length) % total

    frames = []
    for i in idxs:
        frame = reader.get_data(int(i))
        # Convert to grayscale if RGB
        if frame.ndim == 3:
            frame = frame.mean(axis=-1)
        # Resize via PIL (avoid extra dependency)
        from PIL import Image
        img = Image.fromarray(frame.astype(np.uint8)).resize((size, size))
        frames.append(np.asarray(img, dtype=np.float32) / 255.0)
    reader.close()

    clip = np.stack(frames, axis=0)              # (T, H, W)
    clip = clip[None, None, :, :, :]              # (1, 1, T, H, W)
    return torch.from_numpy(clip).float()


def predict_ef(video_path: str) -> Optional[float]:
    """
    Predict LV ejection fraction from an echocardiogram video.

    Returns:
        EF as a percentage (0-100), or None if prediction failed.
    Raises:
        ImportError: if weights are not available. echo.py catches this
        and falls back to Gemma 4.
    """
    model = _load_model()
    if model is None:
        return None

    try:
        clip = _load_clip(video_path).to(_DEVICE)
        with torch.no_grad():
            pred = model(clip)
        ef = float(pred.squeeze().cpu().item())
        # EchoNet outputs raw EF; clamp to physiological range
        return max(0.0, min(100.0, ef))
    except Exception as e:
        print(f"EchoNet prediction failed: {e}")
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python echonet_loader.py <path-to-echo.avi>")
        sys.exit(1)
    ef = predict_ef(sys.argv[1])
    print(f"Predicted EF: {ef}")