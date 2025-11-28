from typing import Optional, Dict, Any
from .db import db as default_db, DatabaseWrapper
from .constitutional_rhythm import RhythmSentry
from .scarlock import ScarLockController

class LivingConstitutionPulse:
    """
    Wraps RhythmSentry and ScarLock into a single 'living' constitutional pulse.
    If drift is detected, ScarLock is engaged automatically.
    """

    def __init__(self, db: Optional[DatabaseWrapper] = None):
        self.db = db or default_db
        self.sentry = RhythmSentry(db=self.db)
        self.lock = ScarLockController(db=self.db)

    def step(self) -> Dict[str, Any]:
        """
        Run one pulse:
        - Use RhythmSentry to check for drift
        - If drift, engage ScarLock
        """
        result = self.sentry.run_cycle()
        if result.get("drift_detected"):
            # Engage global lock with high-level reason
            self.lock.engage_lock(reason="constitution_drift_detected", actor="living_pulse")
            result["lock_engaged"] = True
        else:
            result["lock_engaged"] = self.lock.is_locked()
        return result
