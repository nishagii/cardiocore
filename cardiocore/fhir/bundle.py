# OWNER: Binula
# DAY:   3
# PURPOSE: Assemble a FHIR R4 Bundle containing DiagnosticReport + Observations
#
# The Bundle is the final output of CardioCore â€” what Prompt Opinion agents receive.
#
# Expected interface:
#
#   from fhir.bundle import build_fhir_bundle, get_summary
#
#   bundle = build_fhir_bundle(
#       patient_id="patient-001",
#       ecg_result=ecg_result_dict,    # from inference/ecg.py
#       echo_result=echo_result_dict,  # from inference/echo.py
#       risk_result=risk_result_dict,  # from inference/heart_score.py
#   )
#   # bundle is a valid FHIR R4 Bundle dict with 3 entries:
#   # DiagnosticReport, ECG Observation, Echo Observation
#
#   summary = get_summary(bundle)
#   # returns: {bundle_id, resource_count, summary, triage_tier}

# TODO: Binula implements this on Day 3
# See implementation guide for full code

def build_fhir_bundle(patient_id: str, ecg_result: dict,
                      echo_result: dict, risk_result: dict) -> dict:
    raise NotImplementedError("Binula: implement fhir/bundle.py on Day 3")

def get_summary(bundle: dict) -> dict:
    raise NotImplementedError("Binula: implement fhir/bundle.py on Day 3")
