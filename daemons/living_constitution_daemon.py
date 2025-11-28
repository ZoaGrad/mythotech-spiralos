import time
from core.db import db
from core.living_constitution import LivingConstitutionPulse

def main():
    pulse = LivingConstitutionPulse(db=db)

    while True:
        result = pulse.step()
        print(
            "[LIVING_CONSTITUTION] drift_detected=",
            result.get("drift_detected"),
            "lock_engaged=",
            result.get("lock_engaged"),
        )
        # 60-second heartbeat; adjust if needed
        time.sleep(60)

if __name__ == "__main__":
    main()
