import time
from core.db import db
from core.living_constitution import LivingConstitutionPulse
from core.scarlock import ScarLockController

def main():
    print("[DRIFT_SIM] Starting drift simulation...")
    
    # 1. Manually modify a table to cause drift
    print("[DRIFT_SIM] Injecting drift into teleology_mandates...")
    # We'll just update a row if it exists, or insert a dummy one. 
    # Actually, changing the schema is hard via simple insert. 
    # Let's just insert a row into 'teleology_mandates' which changes the table hash.
    # But wait, 'teleology_mandates' might not exist or might be empty.
    # Let's check if we can just insert a dummy row.
    try:
        db.client._ensure_client().table("teleology_mandates").insert({
            "mandate": "Artificial Drift Injection",
            "priority": 999
        }).execute()
    except Exception as e:
        print(f"[DRIFT_SIM] Failed to insert drift row: {e}")
        # If table doesn't exist or RLS blocks, we might need another way.
        # Let's try to modify 'teleology_weights' which we know exists from migration.
        print("[DRIFT_SIM] Trying teleology_weights instead...")
        db.client._ensure_client().table("teleology_weights").insert({
            "component": "drift_test",
            "weight": 0.0
        }).execute()

    # 2. Run Pulse
    print("[DRIFT_SIM] Running Living Constitution Pulse...")
    pulse = LivingConstitutionPulse(db=db)
    result = pulse.step()
    print(f"[DRIFT_SIM] Pulse result: drift_detected={result.get('drift_detected')}, lock_engaged={result.get('lock_engaged')}")

    # 3. Verify Lock
    lock = ScarLockController(db=db)
    is_locked = lock.is_locked()
    print(f"[DRIFT_SIM] Current Lock Status: {is_locked}")

    if is_locked:
        print("[DRIFT_SIM] SUCCESS: ScarLock engaged.")
    else:
        print("[DRIFT_SIM] FAILURE: ScarLock did NOT engage.")

if __name__ == "__main__":
    main()
