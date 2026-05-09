import base64
import io

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

from PIL import Image

from inference.config import ECG_SNOMED
from inference.gemma4_client import get_client


LEAD_NAMES = [
    "I",
    "II",
    "III",
    "aVR",
    "aVL",
    "aVF",
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6"
]


ECG_SYSTEM = """
You are an expert cardiologist.

Analyze the ECG image carefully.

Respond ONLY with valid JSON.

Allowed rhythm classes:
- NORM
- MI
- STTC
- CD
- HYP
"""


ECG_USER = """
Analyze this ECG image.

Respond ONLY in this JSON format:

{
  "rhythm_class": "NORM|MI|STTC|CD|HYP",
  "confidence": 0.0,
  "clinical_flags": [],
  "reasoning": ""
}
"""


def analyze_from_image_bytes(
    image_bytes: bytes
) -> dict:

    # Validate image
    Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    # Convert image -> base64
    img_b64 = base64.b64encode(
        image_bytes
    ).decode()

    # Send to Gemma multimodal
    response_text = get_client().chat(
        system_prompt=ECG_SYSTEM,
        user_text=ECG_USER,
        images_b64=[img_b64],
        max_tokens=300,
        temperature=0
    )

    # Parse JSON response
    result = get_client().parse_json(
        response_text
    )

    cls = result.get(
        "rhythm_class",
        "NORM"
    )

    # SNOMED mapping
    snomed_code, snomed_desc = ECG_SNOMED.get(
        cls,
        ECG_SNOMED["NORM"]
    )

    return {

        "rhythm_class": cls,

        "confidence": result.get(
            "confidence",
            0.0
        ),

        "all_class_probs": {
            cls: result.get(
                "confidence",
                0.0
            )
        },

        "snomed_code": snomed_code,

        "snomed_description": snomed_desc,

        "clinical_flags": result.get(
            "clinical_flags",
            []
        ),

        "reasoning": result.get(
            "reasoning",
            ""
        ),
    }


def analyze_from_csv(
    csv_path: str
) -> dict:

    signal = pd.read_csv(
        csv_path,
        header=None
    ).values.T.astype("float32")

    rendered = render_signal(signal)

    return analyze_from_image_bytes(
        rendered
    )


def render_signal(
    signal: np.ndarray
) -> bytes:

    fig = plt.figure(
        figsize=(14, 7),
        facecolor="white"
    )

    gs = gridspec.GridSpec(
        6,
        2,
        figure=fig,
        hspace=0.55,
        wspace=0.25
    )

    t = np.linspace(
        0,
        10,
        signal.shape[1]
    )

    for i, lead in enumerate(LEAD_NAMES):

        ax = fig.add_subplot(
            gs[i % 6, i // 6]
        )

        ax.plot(
            t,
            signal[i],
            "k-",
            linewidth=0.7
        )

        ax.set_title(
            lead,
            fontsize=9,
            pad=1
        )

        ax.set_xlim(0, 10)
        ax.set_ylim(-4, 4)

        ax.tick_params(
            labelsize=6
        )

        ax.grid(
            True,
            alpha=0.3,
            color="salmon",
            linestyle=":"
        )

        ax.set_facecolor("#fff8f0")

    buf = io.BytesIO()

    plt.savefig(
        buf,
        format="png",
        dpi=100,
        bbox_inches="tight"
    )

    plt.close(fig)

    return buf.getvalue()
