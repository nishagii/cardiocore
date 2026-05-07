# OWNER: Teammate A
# DAY:   2
# PURPOSE: ECG classification using pretrained PTB-XL classifier + Gemma 4 reasoning
#
# Uses: HuggingFace model 'Syed-Mujtaba-Hassan/ECG-Classification' (88% accuracy on PTB-XL)
#       Gemma 4 for clinical reasoning and flag generation
#
# Expected interface (do not change function names):
#
#   from inference.ecg import analyze_from_image_bytes, analyze_from_csv
#
#   result = analyze_from_image_bytes(png_bytes)
#   # returns: {rhythm_class, confidence, snomed_code, snomed_description,
#   #           clinical_flags, reasoning, all_class_probs}
#
#   result = analyze_from_csv("path/to/12lead.csv")
#   # CSV has 12 columns (one per lead), any number of rows

# TODO: Teammate A implements this on Day 2
# See implementation guide for full code

def analyze_from_image_bytes(image_bytes: bytes) -> dict:
    raise NotImplementedError("Teammate A: implement inference/ecg.py on Day 2")

def analyze_from_csv(csv_path: str) -> dict:
    raise NotImplementedError("Teammate A: implement inference/ecg.py on Day 2")
