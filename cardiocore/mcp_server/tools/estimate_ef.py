# OWNER: Teammate A
# DAY:   2
# PURPOSE: Tool 2 â€” POST /tools/estimate_ejection_fraction
#
# Accepts: multipart/form-data with:
#   file      â€” echo video (AVI or MP4)
#   patient_id â€” optional patient identifier
#
# Flow:
#   1. Read and save uploaded video to temp file
#   2. Call inference/echo.py -> analyze_echo()
#   3. Build FHIR Observation via fhir/echo_observation.py
#   4. Return structured response
#
# Returns:
#   {tool, status, processing_time_ms, result: {
#       ef_percent, ef_source, hf_classification, hf_snomed_code,
#       wall_motion_flags, confidence, patient_id, fhir_observation
#   }}

# TODO: Teammate A implements this on Day 2
# See implementation guide for full code
