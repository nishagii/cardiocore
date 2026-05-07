# OWNER: Teammate A
# DAY:   3
# PURPOSE: Build a FHIR R4 Observation resource for ECG rhythm classification
#
# FHIR spec used:
#   resourceType: Observation
#   code: LOINC 8625-6 (ECG rhythm)
#   valueCodeableConcept: SNOMED CT code from ECG_SNOMED in config.py
#
# Expected interface:
#
#   from fhir.ecg_observation import build_ecg_observation
#   obs = build_ecg_observation(ecg_result_dict, patient_id="patient-001")
#   # returns a valid FHIR R4 Observation dict ready for JSON serialisation

# TODO: Teammate A implements this on Day 3
# See implementation guide for full code

def build_ecg_observation(ecg_result: dict, patient_id: str) -> dict:
    raise NotImplementedError("Teammate A: implement fhir/ecg_observation.py on Day 3")
