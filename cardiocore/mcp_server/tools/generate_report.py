# OWNER: Binula
# DAY:   3
# PURPOSE: Tool 5 â€” POST /tools/generate_cardiac_report
#
# Accepts: JSON body:
#   {
#     patient_id:        "patient-001",
#     ecg_analysis:      {result: {...}},    <- output from Tool 1
#     echo_analysis:     {result: {...}},    <- output from Tool 2
#     risk_stratification: {result: {...}},  <- output from Tool 4
#   }
#
# Flow:
#   1. Extract result dicts from each analysis
#   2. Build FHIR Bundle via fhir/bundle.py
#   3. Validate bundle via fhir/validator.py
#   4. Return bundle + summary
#
# Returns:
#   {tool, status, processing_time_ms, result: {
#       fhir_bundle, bundle_id, resource_count, summary, triage_tier
#   }}

# TODO: Binula implements this on Day 3
# See implementation guide for full code
