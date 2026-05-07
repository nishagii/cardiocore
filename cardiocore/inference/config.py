# CardioCore shared configuration
# Imported by all inference modules and MCP tools
# Edit VLLM_SERVER_URL and SPECIALIST_SERVER_URL in .env after Day 1

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Server URLs â€” set in .env after getting instance IPs on Day 1
VLLM_SERVER_URL       = os.getenv("VLLM_SERVER_URL",       "http://localhost:9000/v1")
SPECIALIST_SERVER_URL = os.getenv("SPECIALIST_SERVER_URL",  "http://localhost:9001")
VLLM_TIMEOUT          = float(os.getenv("VLLM_TIMEOUT", "60"))
HF_TOKEN              = os.getenv("HF_TOKEN")

# ECG class labels (PTB-XL superclasses)
ECG_CLASSES = ["NORM", "MI", "STTC", "CD", "HYP"]

# SNOMED CT codes for each ECG class
ECG_SNOMED = {
    "NORM": ("251139008", "Normal sinus rhythm"),
    "MI":   ("57054005",  "Acute myocardial infarction"),
    "STTC": ("428750005", "ST-T wave change"),
    "CD":   ("44808001",  "Conduction disorder of heart"),
    "HYP":  ("266249003", "Cardiac hypertrophy"),
}

# Heart failure classifications: (snomed_code, description, ef_min, ef_max)
HF_CLASSES = {
    "HFrEF":      ("85232009",  "Heart failure with reduced ejection fraction",   0,  40),
    "HFmrEF":     ("703272007", "Heart failure with mid-range ejection fraction", 40, 50),
    "Borderline": ("40739000",  "Reduced cardiac function",                        50, 55),
    "Normal":     ("72696002",  "Normal cardiac function",                         55, 100),
}

# LOINC codes used in FHIR resources
LOINC_ECG_RHYTHM          = "8625-6"    # ECG rhythm
LOINC_EF                  = "10230-1"   # Left ventricular Ejection fraction
LOINC_CARDIAC_STUDY       = "34552-0"   # Cardiac study
LOINC_CARDIOLOGY_CATEGORY = "11524-6"   # Cardiology category

# Model paths on Instance B
ROOT         = Path(__file__).parent.parent
MODELS_DIR   = ROOT / "models"
ECHOFM_PATH  = MODELS_DIR / "echofm"
ECHONET_PATH = MODELS_DIR / "echonet"

# Gemma 4 system prompts
ECG_SYSTEM_PROMPT = (
    "You are a clinical cardiologist AI assistant specialising in ECG interpretation. "
    "Always respond with valid JSON only. No prose, no markdown fences."
)

ECHO_SYSTEM_PROMPT = (
    "You are a cardiac imaging specialist. "
    "Always respond with valid JSON only. No prose, no markdown fences."
)
