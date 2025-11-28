import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.living_constitution import LivingConstitutionPulse
from core.scarlock import ScarLockController
from core.constitutional_rhythm import ConstitutionHasher, CONSTITUTION_COMPONENTS

def main():
    hasher = ConstitutionHasher(db)
    lock = ScarLockController(db)
    pulse = LivingConstitutionPulse(db=db)

    print("[TEST] Ensuring baseline hashes exist...")
    for component in CONSTITUTION_COMPONENTS:
        h = hasher.record_hash(component)
        print(f"  - {component}: {h}")

    print("[TEST] Checking initial lock status...")
    print("  - is_locked:", lock.is_locked())

    print("[TEST] Running one Living Constitution pulse...")
    result = pulse.step()
    print("[TEST] Pulse result:", result)

    print("[TEST] Final lock status:", lock.is_locked())

if __name__ == "__main__":
    main()
