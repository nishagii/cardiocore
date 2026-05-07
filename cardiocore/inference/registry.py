# Singleton registry â€” models loaded once at startup, reused for every request
# No changes needed here â€” just import from this module

import threading

_lock          = threading.Lock()
_heart_scorer  = None


def get_heart_scorer():
    """Returns the shared HEARTScorer instance."""
    global _heart_scorer
    if _heart_scorer is None:
        with _lock:
            if _heart_scorer is None:
                from inference.heart_score import HEARTScorer
                _heart_scorer = HEARTScorer()
    return _heart_scorer
