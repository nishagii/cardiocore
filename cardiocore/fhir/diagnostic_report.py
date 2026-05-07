# OWNER: Binula
# DAY:   3
# PURPOSE: Build a FHIR R4 DiagnosticReport resource
#
# FHIR spec used:
#   resourceType: DiagnosticReport
#   code: LOINC 34552-0 (Cardiac study)
#   result: references to ECG and Echo Observation resources
#   conclusion: human-readable triage summary
#   extension: triage-tier (string) and heart-score (integer)
#
# Expected interface:
#
#   from fhir.diagnostic_report import build_diagnostic_report
#   report = build_diagnostic_report(patient_id, ecg_obs, echo_obs, risk_result)
#   # returns a valid FHIR R4 DiagnosticReport dict

# TODO: Binula implements this on Day 3
# See implementation guide for full code

def build_diagnostic_report(patient_id: str, ecg_obs: dict,
                             echo_obs: dict, risk_result: dict) -> dict:
    raise NotImplementedError("Binula: implement fhir/diagnostic_report.py on Day 3")
