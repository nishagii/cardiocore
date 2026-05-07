# OWNER: Teammate A
# DAY:   2
# PURPOSE: Tool 3 â€” POST /tools/analyze_cardiac_structure
#
# Accepts: multipart/form-data with:
#   file      â€” echo video (AVI or MP4)
#   patient_id â€” optional patient identifier
#
# Flow:
#   1. Read and save uploaded video to temp file
#   2. Call inference/echo_structure.py -> analyze_structure()
#   3. Return structured response
#
# Returns:
#   {tool, status, processing_time_ms, result: {
#       lv_size, wall_thickness, structural_flags,
#       pericardial_effusion, confidence, reasoning, patient_id
#   }}

# TODO: Teammate A implements this on Day 2
# See implementation guide for full code
