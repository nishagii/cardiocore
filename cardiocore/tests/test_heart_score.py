# OWNER: Binula
# DAY:   4
# PURPOSE: Tests for HEART score formula
#
# Run with: pytest tests/test_heart_score.py -v

import pytest
from inference.heart_score import HEARTScorer

# TODO: Binula implements these tests on Day 4
# Expected tests:
#   test_low_risk()   - score=0, tier=Normal
#   test_high_risk()  - score=10, tier=Urgent
#   test_moderate()   - score=5, tier=Routine
#   test_components_sum() - sum of components equals total score
#   test_age_thresholds() - age 44=0pts, 45=1pt, 65=2pts
#   test_mi_override()    - ecg_class=MI forces Urgent regardless of score

def test_placeholder():
    # Remove this and add real tests on Day 4
    assert True
