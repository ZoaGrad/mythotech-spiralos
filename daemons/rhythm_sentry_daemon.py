from core.constitutional_rhythm import RhythmSentry
from core.db import db
import time

def main():
    sentry = RhythmSentry(db=db)
    while True:
        result = sentry.run_cycle()
        # You can swap this for structured logging
        print("[RHYTHM_DAEMON] drift_detected:", result["drift_detected"])
        time.sleep(60)

if __name__ == "__main__":
    main()
