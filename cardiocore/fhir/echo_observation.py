# OWNER: Teammate A
# DAY:   3
# PURPOSE: Build a FHIR R4 Observation resource for ejection fraction
#
# FHIR spec used:
#   resourceType: Observation
#   code: LOINC 10230-1 (Left ventricular Ejection fraction)
#   valueQuantity: {value: ef_percent, unit: "%", system: UCUM}
#
# Expected interface:
#
#   from fhir.echo_observation import build_echo_observation
#   obs = build_echo_observation(echo_result_dict, patient_id="patient-001")
#   # returns a valid FHIR R4 Observation dict

# TODO: Teammate A implements this on Day 3
# See implementation guide for full code

def build_echo_observation(echo_result: dict, patient_id: str) -> dict:
    raise NotImplementedError("Teammate A: implement fhir/echo_observation.py on Day 3")
