# OWNER: Binula
# DAY:   3
# PURPOSE: Tool 4 â€” POST /tools/risk_stratify
#
# Accepts: JSON body:
#   {
#     ecg_analysis:     {result: {rhythm_class, confidence, ...}},
#     echo_analysis:    {result: {ef_percent, hf_classification, ...}},
#     clinical_context: {age, known_conditions, troponin_ratio, history_suspicion}
#   }
#
# Flow:
#   1. Extract ECG class and map to HEART ECG component score
#   2. Extract EF and apply critical override rules (MI or EF<35 -> Urgent)
#   3. Run HEARTScorer.compute() with all inputs
#   4. Return structured response
#
# Returns:
#   {tool, status, processing_time_ms, result: {
#       heart_score, component_scores, triage_tier,
#       mace_10day_probability, recommended_action
#   }}

# TODO: Binula implements this on Day 3
# See implementation guide for full code
