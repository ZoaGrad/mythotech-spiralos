import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.constitutional_rhythm import ConstitutionHasher, ConstitutionVerifier, RhythmSentry

from core.db import db

def main():
    hasher = ConstitutionHasher(db)
    verifier = ConstitutionVerifier(db)
    sentry = RhythmSentry(db=db)

    print("[TEST] Recording hashes for all constitution components...")
    for component in [
        "teleology_mandates",
        "structural_operation_whitelist",
        "structural_change_requests",
        "structural_snapshots",
        "structural_safety_policies",
        "proposal_patterns",
        "autopoiesis_log",
        "rollback_journal",
        "teleology_weights",
        "quantum_tags",
        "system_reflections",
        "paradox_events",
        "paradox_resolutions",
    ]:
        h = hasher.record_hash(component)
        print(f"  - {component}: {h}")

    print("[TEST] Verifying immediately (should all be OK)...")
    for component in [
        "teleology_mandates",
        "structural_operation_whitelist",
        "structural_change_requests",
        "structural_snapshots",
        "structural_safety_policies",
        "proposal_patterns",
        "autopoiesis_log",
        "rollback_journal",
        "teleology_weights",
        "quantum_tags",
        "system_reflections",
        "paradox_events",
        "paradox_resolutions",
    ]:
        result = verifier.verify_component(component)
        print(f"  - {component}: {result['status']}")

    print("[TEST] Running one Rhythm cycle...")
    cycle = sentry.run_cycle()
    print("[TEST] Rhythm result:", cycle)

if __name__ == "__main__":
    main()
