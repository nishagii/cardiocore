# OWNER: Binula
# DAY:   2
# PURPOSE: Pure Python HEART score formula â€” no ML, no GPU required
#
# HEART score components (each 0-2 points, total 0-10):
#   H â€” History (suspicion of ACS)
#   E â€” ECG findings
#   A â€” Age
#   R â€” Risk factors
#   T â€” Troponin level
#
# Score interpretation:
#   0-3  = Low    = Normal tier    = < 2% 10-day MACE
#   4-6  = Moderate = Routine tier = 12-65% 10-day MACE
#   7-10 = High   = Urgent tier    = > 50% 10-day MACE
#
# Expected interface:
#
#   from inference.heart_score import HEARTScorer
#   scorer = HEARTScorer()
#   result = scorer.compute({
#       "history_suspicion": "highly_suspicious",   # or "moderately" or "slightly_nonspecific"
#       "ecg_result": "significant_deviation",       # or "nonspecific_repol" or "normal"
#       "age": 67,
#       "risk_factors": ["diabetes", "hypertension"],
#       "troponin_ratio": 2.8,                       # troponin / upper limit of normal
#   })
#   # returns: {heart_score, component_scores, triage_tier,
#   #           mace_10day_probability, recommended_action}

# TODO: Binula implements this on Day 2
# See implementation guide for full code

class HEARTScorer:
    def compute(self, patient_data: dict) -> dict:
        raise NotImplementedError("Binula: implement HEARTScorer in inference/heart_score.py on Day 2")
