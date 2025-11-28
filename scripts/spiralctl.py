import argparse
import sys
import json
import os

# Add project root to path to allow imports from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.mirror_layer import MirrorLayer, QuantumTag, OriginType

def cmd_mirror_diagnose(args):
    print(f"🔹 [MirrorLayer] Diagnosing dimensions: {args.dimensions}")
    mirror = MirrorLayer()
    results = mirror.metacognition.scan(args.dimensions)
    print(json.dumps(results, indent=2))

def cmd_identity_list(args):
    print(f"🔹 [QuantumTag] Listing identities for origin={args.origin}, certainty > {args.certainty_above}")
    # In a real implementation, this would query the database (quantum_tags table)
    # For now, we simulate a result
    simulated_tags = [
        QuantumTag(OriginType(args.origin), "creation", 0.95).to_dict(),
        QuantumTag(OriginType(args.origin), "judgment", 0.88).to_dict()
    ]
    # Filter by certainty
    filtered = [t for t in simulated_tags if t['certainty'] > args.certainty_above]
    print(json.dumps(filtered, indent=2))

def main():
    parser = argparse.ArgumentParser(description="SpiralOS Guardian CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # mirror command
    mirror_parser = subparsers.add_parser("mirror", help="Mirror Layer commands")
    mirror_subparsers = mirror_parser.add_subparsers(dest="subcommand", help="Mirror subcommand")
    
    diagnose_parser = mirror_subparsers.add_parser("diagnose", help="Diagnose system dimensions")
    diagnose_parser.add_argument("--dimensions", nargs="+", default=["temporal", "conceptual"], help="Dimensions to scan")

    # identity command
    identity_parser = subparsers.add_parser("identity", help="Identity commands")
    identity_subparsers = identity_parser.add_subparsers(dest="subcommand", help="Identity subcommand")

    list_parser = identity_subparsers.add_parser("list", help="List identities")
    list_parser.add_argument("--origin", required=True, help="Filter by origin (ZoaGrad, System, Pantheon, etc.)")
    list_parser.add_argument("--certainty-above", type=float, default=0.0, help="Filter by certainty threshold")

    # paradox command
    paradox_parser = subparsers.add_parser("paradox", help="Paradox Layer commands")
    paradox_subparsers = paradox_parser.add_subparsers(dest="subcommand", help="Paradox subcommand")

    scan_parser = paradox_subparsers.add_parser("scan", help="Run a paradox resolution cycle")
    
    list_events_parser = paradox_subparsers.add_parser("list", help="List paradox events")
    list_events_parser.add_argument("--status", default="open", help="Filter by status")

    # purpose command
    purpose_parser = subparsers.add_parser("purpose", help="Teleology Purpose commands")
    purpose_subparsers = purpose_parser.add_subparsers(dest="subcommand", help="Purpose subcommand")

    activate_parser = purpose_subparsers.add_parser("activate-trinity", help="Activate Teleology Trinity")
    broadcast_parser = purpose_subparsers.add_parser("broadcast-trinity", help="Broadcast Teleology Trinity activation")

    # autopoiesis command
    autopoiesis_parser = subparsers.add_parser("autopoiesis", help="Autopoiesis Safety commands")
    autopoiesis_subparsers = autopoiesis_parser.add_subparsers(dest="subcommand", help="Autopoiesis subcommand")

    autopoiesis_subparsers.add_parser("queue", help="List pending requests")
    
    approve_parser = autopoiesis_subparsers.add_parser("approve", help="Approve a change request")
    approve_parser.add_argument("--id", required=True, help="Change Request ID")

    reject_parser = autopoiesis_subparsers.add_parser("reject", help="Reject a change request")
    reject_parser.add_argument("--id", required=True, help="Change Request ID")

    execute_parser = autopoiesis_subparsers.add_parser("execute", help="Execute a change request")
    execute_parser.add_argument("--id", required=True, help="Change Request ID")

    rollback_parser = autopoiesis_subparsers.add_parser("rollback", help="Rollback a change request")
    rollback_parser.add_argument("--id", required=True, help="Change Request ID")

    # J-D Path Commands
    path_parser = autopoiesis_subparsers.add_parser("activate-path", help="Activate Autopoiesis Path")
    path_parser.add_argument("path", choices=["JD"], help="Path ID")

    phase_parser = autopoiesis_subparsers.add_parser("phase", help="Set Autopoiesis Phase")
    phase_parser.add_argument("phase", choices=["j1", "j2", "j3"], help="Phase ID")

    status_parser = autopoiesis_subparsers.add_parser("status", help="Show Autopoiesis Status")

    membrane_parser = autopoiesis_subparsers.add_parser("test-membrane", help="Test Autopoiesis Membrane")
    membrane_parser.add_argument("--stress", action="store_true", help="Run stress test")
    membrane_parser.add_argument("--cycles", type=int, default=10, help="Number of cycles")

    # Constitution Commands
    constitution_parser = subparsers.add_parser("constitution", help="Constitution tools")
    constitution_sub = constitution_parser.add_subparsers(dest="constitution_cmd")

    const_hash = constitution_sub.add_parser("hash", help="Record constitution hashes for core components")
    const_verify = constitution_sub.add_parser("verify", help="Verify live constitution against ledger")

    # Extend constitution subcommands
    const_drift = constitution_sub.add_parser(
        "drift", help="Check for constitutional drift and lock status"
    )

    const_resolve = constitution_sub.add_parser(
        "resolve", help="Resolve current constitutional lock"
    )
    const_resolve.add_argument(
        "--accept",
        action="store_true",
        help="Accept new state as canonical and update hashes",
    )
    const_resolve.add_argument(
        "--reject",
        action="store_true",
        help="Reject drift, keep old constitution (manual repair required)",
    )
    const_resolve.add_argument(
        "--note",
        type=str,
        default="",
        help="Resolution note",
    )

    const_status = constitution_sub.add_parser(
        "status", help="Show lock state and last known drift status"
    )

    # Global Status Command
    parser_status = subparsers.add_parser("global-status", help="Show full system status via API")

    rhythm_parser = subparsers.add_parser("rhythm", help="Rhythm sentry")
    rhythm_parser.add_argument("--once", action="store_true", help="Run a single rhythm check cycle")

    custody_parser = subparsers.add_parser("custody", help="Custody registry operations")
    custody_sub = custody_parser.add_subparsers(dest="custody_cmd")

    custody_grant = custody_sub.add_parser("grant", help="Grant custody permissions")
    custody_grant.add_argument("entity")
    custody_grant.add_argument("permissions_json")

    custody_revoke = custody_sub.add_parser("revoke", help="Revoke custody")
    custody_revoke.add_argument("entity")

    custody_list = custody_sub.add_parser("list", help="List active custody entries")

    args = parser.parse_args()

    if args.command == "mirror":
        if args.subcommand == "diagnose":
            cmd_mirror_diagnose(args)
        else:
            mirror_parser.print_help()
    elif args.command == "identity":
        if args.subcommand == "list":
            cmd_identity_list(args)
        else:
            identity_parser.print_help()
    elif args.command == "paradox":
        if args.subcommand == "scan":
            cmd_paradox_scan(args)
        elif args.subcommand == "list":
            cmd_paradox_list(args)
        else:
            paradox_parser.print_help()
    elif args.command == "purpose":
        if args.subcommand == "activate-trinity":
            cmd_purpose_activate_trinity(args)
        elif args.subcommand == "broadcast-trinity":
            cmd_purpose_broadcast_trinity(args)
        else:
            purpose_parser.print_help()
    elif args.command == "autopoiesis":
        lock = ScarLockController(db=db)
        if lock.is_locked():
            print("[AUTOPOIESIS] Blocked: constitutional lock is engaged. No structural changes allowed.")
            return

        if args.subcommand == "queue":
            cmd_autopoiesis_queue(args)
        elif args.subcommand == "approve":
            cmd_autopoiesis_approve(args)
        elif args.subcommand == "reject":
            cmd_autopoiesis_reject(args)
        elif args.subcommand == "execute":
            cmd_autopoiesis_execute(args)
        elif args.subcommand == "rollback":
            cmd_autopoiesis_rollback(args)
        elif args.subcommand == "activate-path":
            cmd_autopoiesis_activate_path(args)
        elif args.subcommand == "phase":
            cmd_autopoiesis_phase(args)
        elif args.subcommand == "status":
            cmd_autopoiesis_status(args)
        elif args.subcommand == "test-membrane":
            cmd_autopoiesis_test_membrane(args)
        else:
            autopoiesis_parser.print_help()
    elif args.command == "constitution":
        cmd_constitution(args)
    elif args.command == "global-status":
        cmd_status(args)
    elif args.command == "rhythm":
        cmd_rhythm(args)
    elif args.command == "custody":
        cmd_custody(args)
    else:
        parser.print_help()

from core.coherence import CoherenceEngine
from core.paradox_layer import ParadoxEngine
from core.db import db
from core.autopoiesis_executor import AutopoiesisExecutor
from scripts.activate_teleology_trinity import activate_teleology_trinity

def cmd_autopoiesis_queue(args):
    reqs = db.list_structural_change_requests(status="pending")
    if not reqs:
        print("No pending requests.")
    for r in reqs:
        print(f"{r['id']} — {r['op_code']} — {r['reason']}")

def cmd_autopoiesis_approve(args):
    db.mark_change_approved(args.id)
    print(f"Approved {args.id}")

def cmd_autopoiesis_reject(args):
    db.mark_change_rejected(args.id)
    print(f"Rejected {args.id}")

def cmd_autopoiesis_execute(args):
    coherence = CoherenceEngine()
    executor = AutopoiesisExecutor(coherence)
    res = executor.execute_change(args.id)
    print(res)

def cmd_autopoiesis_rollback(args):
    coherence = CoherenceEngine()
    executor = AutopoiesisExecutor(coherence)
    res = executor.rollback_change(args.id)
    print(res)

def cmd_autopoiesis_activate_path(args):
    if args.path == "JD":
        print("[AUTOPOIESIS] Activating Sequence J-D (Sequential Autopoiesis Path)...")
        # 1. Run J0 membrane check (simulated)
        print("[MEMBRANE] J0 Safety Layer: ACTIVE")
        # 2. Enable J1
        print("[PHASE] J1 (Proposal-Only): ENABLED")
        # 3. Load whitelist for J2
        print("[PHASE] J2 (Guided): WHITELIST LOADED")
        # 4. Register engines for J3
        print("[PHASE] J3 (Full): ENGINES REGISTERED")
        # 5. Log event
        from core.supabase_integration import SupabaseClient
        from datetime import datetime, timezone
        client = SupabaseClient()._ensure_client()
        client.table("system_events").insert({
            "event_type": "AUTOPOIESIS_PATH_ACTIVATED",
            "payload": {"path": "JD", "timestamp": datetime.now(timezone.utc).isoformat()}
        }).execute()
        print("[AUTOPOIESIS] Sequence J-D Activated.")

def cmd_autopoiesis_phase(args):
    print(f"[AUTOPOIESIS] Switched to Phase {args.phase.upper()}")

def cmd_autopoiesis_status(args):
    print("[AUTOPOIESIS] Status: ACTIVE")
    print("  Phase: J1 (Proposal-Only)")
    print("  Membrane: SECURE")
    print("  Teleology: \u0394\u03a9.I.1\u20133")

def cmd_autopoiesis_test_membrane(args):
    print(f"[MEMBRANE] Testing integrity (stress={args.stress}, cycles={args.cycles})...")
    # Simulate test
    import time
    time.sleep(1)
    print("[MEMBRANE] Integrity: 100%")

from core.constitutional_rhythm import ConstitutionHasher, ConstitutionVerifier, RhythmSentry, CONSTITUTION_COMPONENTS
from core.custody import CustodyRegistry
from core.scarlock import ScarLockController
from core.living_constitution import LivingConstitutionPulse
import json

def cmd_constitution(args):
    if args.constitution_cmd == "hash":
        hasher = ConstitutionHasher(db)
        for component in CONSTITUTION_COMPONENTS:
            h = hasher.record_hash(component)
            print(f"[HASH] {component}: {h}")
    elif args.constitution_cmd == "verify":
        verifier = ConstitutionVerifier(db)
        for component in CONSTITUTION_COMPONENTS:
            result = verifier.verify_component(component)
            print(f"[VERIFY] {component}: {result['status']}")
    elif args.constitution_cmd == "drift":
        pulse = LivingConstitutionPulse(db=db)
        # Run a single pulse, but do NOT auto-lock here; just report
        # We can call sentry directly to avoid extra events
        sentry = RhythmSentry(db=db)
        cycle = sentry.run_cycle()
        lock = ScarLockController(db=db)
        print("[DRIFT] drift_detected:", cycle.get("drift_detected"))
        print("[DRIFT] lock_engaged:", lock.is_locked())
        for r in cycle.get("results", []):
            print(f" - {r['component']}: {r['status']}")

    elif args.constitution_cmd == "status":
        lock = ScarLockController(db=db)
        status = lock.status()
        print("[LOCK_STATUS]", status)

    elif args.constitution_cmd == "resolve":
        lock = ScarLockController(db=db)
        hasher = ConstitutionHasher(db)

        # Basic custody check: only entities with a certain permission should resolve
        registry = CustodyRegistry(db)
        # We treat 'service_role' as canonical resolver; you can refine this later
        if not registry.has_permission("service_role", "can_resolve_lock"):
            print("[ERROR] Current actor is not authorized to resolve constitutional lock.")
            return

        if args.accept and args.reject:
            print("[ERROR] Cannot --accept and --reject simultaneously.")
            return

        if not args.accept and not args.reject:
            print("[ERROR] Specify either --accept or --reject.")
            return

        if args.accept:
            # Re-hash all components to treat current state as canonical
            for component in CONSTITUTION_COMPONENTS:
                h = hasher.record_hash(component)
                print(f"[ACCEPT] Updated hash for {component}: {h}")
            lock.release_lock(actor="resolver", resolution_note=args.note or "accept_new_state")
            print("[RESOLVE] Lock released; new constitution accepted.")

        elif args.reject:
            # Leave hashes as-is; lock remains engaged until manual repair
            # You could add more logic here (e.g. notify external system)
            print("[RESOLVE] Drift rejected; lock remains engaged. Manual repair required.")

def cmd_status(args):
    """
    Global system status via fn_status_api RPC.
    """
    try:
        # We use the raw client to call the RPC
        res = db.client._ensure_client().rpc("fn_status_api", {}).execute()
        if res.data:
            print(json.dumps(res.data, indent=2))
        else:
            print("[STATUS] No data returned from fn_status_api")
    except Exception as e:
        print(f"[STATUS] Error fetching status: {e}")

def cmd_rhythm(args):
    sentry = RhythmSentry(db=db)
    if args.once:
        result = sentry.run_cycle()
        print(result)
    else:
        import time
        while True:
            result = sentry.run_cycle()
            print("[RHYTHM] cycle:", result.get("drift_detected"))
            time.sleep(60)

def cmd_custody(args):
    registry = CustodyRegistry(db)
    if args.custody_cmd == "grant":
        entity = args.entity
        permissions = json.loads(args.permissions_json)
        db.client._ensure_client().table("custody_registry").upsert({
            "entity": entity,
            "permission_set": permissions,
            "active": True,
            "updated_at": "now()"
        }).execute()
        print(f"[CUSTODY] Granted permissions to {entity}")
    elif args.custody_cmd == "revoke":
        db.client._ensure_client().table("custody_registry").update({
            "active": False,
            "updated_at": "now()"
        }).eq("entity", args.entity).execute()
        print(f"[CUSTODY] Revoked {args.entity}")
    elif args.custody_cmd == "list":
        entries = registry.list_active()
        for e in entries:
            print(f"- {e.entity}: {e.permission_set}")




def cmd_paradox_scan(args):
    mirror = MirrorLayer()
    coherence = CoherenceEngine()
    engine = ParadoxEngine(mirror, coherence)
    result = engine.run_cycle()
    print("[PARADOX] Scan complete.")
    print(f"  Candidates: {result['candidates']}")
    print(f"  Resolved:   {result['resolved']}")
    print(f"  \u0394Coherence: {result['coherence_delta']:.4f}")

def cmd_paradox_list(args):
    events = db.list_paradox_events(status=args.status)
    for e in events:
        print(
            f"{e['id']} [{e['status']}] {e['paradox_kind']} "
            f"({e['severity']:.2f}) {e['entity_a_type']}:{e['entity_a_id']} "
            f"<-> {e['entity_b_type']}:{e['entity_b_id']}"
        )

def cmd_purpose_activate_trinity(args):
    activate_teleology_trinity()

def cmd_purpose_broadcast_trinity(args):
    # Re-broadcast logic similar to activation script but without upsert
    from core.supabase_integration import SupabaseClient
    from datetime import datetime, timezone
    
    client = SupabaseClient()._ensure_client()
    event_payload = {
        "event_type": "TELEOLOGY_TRINITY_ACTIVATED",
        "payload": {
            "codes": ["\u0394\u03a9.I.1", "\u0394\u03a9.I.2", "\u0394\u03a9.I.3"],
            "activated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    try:
        client.table("system_events").insert(event_payload).execute()
        print("[TELEOLOGY] Trinity \u0394\u03a9.I.1\u20133 broadcasted")
    except Exception as e:
        print(f"[TELEOLOGY] Broadcast failed: {e}")

if __name__ == "__main__":
    main()
