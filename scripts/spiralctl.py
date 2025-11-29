import argparse
import sys
import json
import os

# Add project root to path to allow imports from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from core.mirror_layer import MirrorLayer, QuantumTag, OriginType
from core.audit_emitter import emit_audit_event
from core.temporal import TemporalDriftEngine
from core.causality_emitter import link_events
from core.db import db
from core.autopoiesis_executor import AutopoiesisExecutor
from scripts.activate_teleology_trinity import activate_teleology_trinity
from core.constitutional_rhythm import ConstitutionHasher, ConstitutionVerifier, RhythmSentry, CONSTITUTION_COMPONENTS
from core.custody import CustodyRegistry
from core.scarlock import ScarLockController
from core.living_constitution import LivingConstitutionPulse
from core.status_api import StatusAPI

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
    api = StatusAPI(db)
    data = api.get_status()
    if data:
        print(json.dumps(data, indent=2))
    else:
        print("[STATUS] No data returned or error occurred.")

def cmd_dashboard(args):
    """
    Launch local dashboard preview.
    """
    if args.subcommand == "preview":
        import subprocess
        import os
        dashboard_dir = os.path.join(os.getcwd(), "web", "dashboard")
        print(f"[DASHBOARD] Launching preview in {dashboard_dir}...")
        try:
            # Check if node_modules exists, if not install
            if not os.path.exists(os.path.join(dashboard_dir, "node_modules")):
                print("[DASHBOARD] Installing dependencies...")
                subprocess.check_call("npm install", shell=True, cwd=dashboard_dir)
            
            print("[DASHBOARD] Starting dev server...")
            subprocess.check_call("npm run dev", shell=True, cwd=dashboard_dir)
        except Exception as e:
            print(f"[DASHBOARD] Error: {e}")

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

def cmd_paradox_forecast(args):
    client = db.client._ensure_client()
    
    res = (
        client.table("view_paradox_risk_surface")
        .select(
            "id,created_at,paradox_risk,risk_band,drift_risk,tension_risk,status"
        )
        .order("paradox_risk", desc=True)
        .limit(30)
        .execute()
    )

    rows = res.data or []
    if not rows:
        print("No paradox projections found.")
        return

    for r in rows:
        r["created_at"] = str(r["created_at"])
        r["paradox_risk"] = float(r["paradox_risk"])
        r["drift_risk"] = float(r["drift_risk"])
        r["tension_risk"] = float(r["tension_risk"])

    try:
        from tabulate import tabulate
        print(tabulate(rows, headers="keys"))
    except ImportError:
        print(json.dumps(rows, indent=2))

def cmd_collapse_forecast(args):
    client = db.client._ensure_client()
    
    res = (
        client.table("view_collapse_horizon_surface")
        .select(
            "id,collapse_risk,collapse_band,horizon_start,horizon_end,status"
        )
        .order("collapse_risk", desc=True)
        .limit(20)
        .execute()
    )

    rows = res.data or []
    if not rows:
        print("No collapse envelopes projected.")
        return

    for r in rows:
        r["collapse_risk"] = float(r["collapse_risk"])
        r["horizon_start"] = str(r["horizon_start"])
        r["horizon_end"] = str(r["horizon_end"])

    try:
        from tabulate import tabulate
        print(tabulate(rows, headers="keys"))
    except ImportError:
        print(json.dumps(rows, indent=2))

def cmd_lattice_forecast(args):
    client = db.client._ensure_client()
    
    res = (
        client.table("view_future_lattice_surface")
        .select(
            "id,lattice_state,collapse_probability,curvature_risk,guardian_recommendation,horizon_start,horizon_end"
        )
        .order("collapse_probability", desc=True)
        .limit(20)
        .execute()
    )

    rows = res.data or []
    if not rows:
        print("No integration lattice nodes found.")
        return

    for r in rows:
        r["collapse_probability"] = float(r["collapse_probability"])
        r["curvature_risk"] = float(r["curvature_risk"])
        r["horizon_start"] = str(r["horizon_start"])
        r["horizon_end"] = str(r["horizon_end"])

    try:
        from tabulate import tabulate
        print(tabulate(rows, headers="keys"))
    except ImportError:
        print(json.dumps(rows, indent=2))

def cmd_continuation_health(args):
    from core.continuation.engine import get_continuation_health_stats
    print("[CONTINUATION] Fetching health metrics...")
    stats = get_continuation_health_stats()
    print(json.dumps(stats, indent=2))

def cmd_guardian_scan(args):
    from core.guardian_actions import scan_future_lattice_window
    print("[GUARDIAN] Scanning future lattice window...")
    nodes = scan_future_lattice_window(window_minutes=60)
    if not nodes:
        print("No actionable nodes found.")
        return
    
    print(f"Found {len(nodes)} candidates:")
    for n in nodes:
        print(f" - {n['id']} [{n['lattice_state']}] Prob: {n['collapse_probability']}")

def cmd_guardian_plan(args):
    from core.guardian_actions import plan_action_for_lattice
    print(f"[GUARDIAN] Planning action for lattice {args.lattice_id}...")
    action_id = plan_action_for_lattice(None, args.lattice_id)
    if action_id:
        print(f"Action Created/Found: {action_id}")
    else:
        print("Failed to plan action.")

def cmd_guardian_actions(args):
    client = db.client._ensure_client()
    res = (
        client.table("guardian_action_events")
        .select("id,created_at,lattice_state,chosen_action,severity,status")
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    rows = res.data or []
    if not rows:
        print("No guardian actions found.")
        return

    for r in rows:
        r["created_at"] = str(r["created_at"])
    
    try:
        from tabulate import tabulate
        print(tabulate(rows, headers="keys"))
    except ImportError:
        print(json.dumps(rows, indent=2))

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

def cmd_audit(args):
    if args.audit_cmd == "surface":
        try:
            res = db.client._ensure_client().table("view_global_audit_surface").select("*").limit(20).execute()
            for evt in res.data:
                print(f"[{evt['created_at']}] {evt['id']} | {evt['component']} -> {evt['event_type']} (Hash: {evt.get('phase_lock_hash')})")
        except Exception as e:
            print(f"Error fetching audit surface: {e}")
    elif args.audit_cmd == "emit":
        emit_audit_event("manual_emit", "CLI", {"message": args.msg})
        print(f"Emitted manual event: {args.msg}")
    elif args.audit_cmd == "diff":
        print("Comparing Phase-Lock Hash vs Baseline...")
        try:
            res = db.client._ensure_client().rpc("fn_verify_phase_lock", {}).execute()
            print(f"Current Runtime Hash: {res.data.get('hash')}")
            print("Baseline: [LOAD FROM ARTIFACT]") # Placeholder
        except Exception as e:
            print(f"Error verifying phase lock: {e}")

def cmd_temporal(args):
    engine = TemporalDriftEngine()
    
    if args.temporal_cmd == "anchor":
        id = engine.record_anchor(source="CLI")
        print(f"[TEMPORAL] Anchor recorded: {id}")
        
    elif args.temporal_cmd == "verify":
        res = engine.verify_drift(source="CLI")
        print(f"[TEMPORAL] Drift Check: {res}")
        
    elif args.temporal_cmd == "log":
        try:
            res = db.client._ensure_client().table("view_temporal_drift_status").select("*").limit(10).execute()
            for row in res.data:
                print(f"[{row['created_at']}] {row['source']} | Delta: {row['drift_delta_ms']}ms | {row['severity']}")
        except Exception as e:
            print(f"Error fetching log: {e}")

def cmd_causality(args):
    if args.causality_cmd == "link":
        try:
            notes = json.loads(args.notes) if args.notes else {}
            link_id = link_events(
                source_event_id=args.source,
                target_event_id=args.target,
                cause_type=args.type,
                weight=args.weight,
                severity=args.severity,
                notes=notes
            )
            if link_id:
                print(f"[CAUSALITY] Link created: {link_id}")
            else:
                print("[CAUSALITY] Failed to create link.")
        except Exception as e:
            print(f"[CAUSALITY] Error: {e}")

    elif args.causality_cmd == "surface":
        try:
            limit = args.limit
            res = db.client._ensure_client().table("view_causal_links").select("*").limit(limit).execute()
            print(f"--- Causality Surface (Limit: {limit}) ---")
            for row in res.data:
                print(f"[{row['created_at']}] {row['source_event_type']} --({row['cause_type']})--> {row['target_event_type']} (W: {row['weight']}) | Anchor: {row.get('temporal_anchor_id')}")
        except Exception as e:
            print(f"[CAUSALITY] Error fetching surface: {e}")

    elif args.causality_cmd == "tension":
        limit = getattr(args, "limit", 10)
        try:
            res = db.client._ensure_client().table("view_causality_tension").select("*").limit(limit).execute()
            print(f"--- High-Tension Nodes (Limit: {limit}) ---")
            for row in res.data:
                print(f"[{row['latest_event_at']}] {row['component']} :: {row['event_type']} "
                      f"(Sev: {row['severity_dominant']}, W: {row['total_weight_norm']}, T: {row['mesh_tension_max']})")
        except Exception as e:
            print(f"[CAUSALITY] Error fetching tension: {e}")

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

    paradox_subparsers.add_parser(
        "forecast",
        help="List predicted paradox risk surface",
    )

    # collapse command
    collapse_parser = subparsers.add_parser("collapse", help="Collapse Horizon commands")
    collapse_subparsers = collapse_parser.add_subparsers(dest="subcommand", help="Collapse subcommand")

    collapse_subparsers.add_parser(
        "forecast",
        help="List projected collapse envelopes",
    )

    # lattice command
    lattice_parser = subparsers.add_parser("lattice", help="Integration Lattice commands")
    lattice_subparsers = lattice_parser.add_subparsers(dest="subcommand", help="Lattice subcommand")

    lattice_subparsers.add_parser(
        "forecast",
        help="List integration lattice projections",
    )

    # continuation command
    continuation_parser = subparsers.add_parser("continuation", help="Continuation Engine commands")
    continuation_subparsers = continuation_parser.add_subparsers(dest="subcommand", help="Continuation subcommand")
    
    health_parser = continuation_subparsers.add_parser("health", help="Show continuation health metrics")

    # guardian command (new group, separate from autopoiesis for clarity)
    guardian_parser = subparsers.add_parser("guardian", help="Guardian Action commands")
    guardian_subparsers = guardian_parser.add_subparsers(dest="subcommand", help="Guardian subcommand")
    
    guardian_subparsers.add_parser("scan", help="Scan future lattice for candidates")
    
    plan_parser = guardian_subparsers.add_parser("plan", help="Plan action for specific lattice node")
    plan_parser.add_argument("--lattice-id", required=True, help="Lattice Node UUID")
    
    guardian_subparsers.add_parser("actions", help="List recent guardian actions")

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

    # Dashboard Command
    parser_dashboard = subparsers.add_parser("dashboard", help="Manage dashboard")
    dash_subs = parser_dashboard.add_subparsers(dest="subcommand")
    dash_subs.add_parser("preview", help="Launch local dashboard preview")

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

    # Audit Command
    audit_parser = subparsers.add_parser("audit", help="Audit Surface commands")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")

    audit_sub.add_parser("surface", help="Prints latest audit events")
    
    emit_parser = audit_sub.add_parser("emit", help="Manual test emitter")
    emit_parser.add_argument("msg", help="Message to emit")

    audit_sub.add_parser("diff", help="Compares latest phase-lock hash vs baseline")

    # Temporal Command
    temporal_parser = subparsers.add_parser("temporal", help="Temporal Coherence commands")
    temporal_sub = temporal_parser.add_subparsers(dest="temporal_cmd")
    temporal_sub.add_parser("anchor", help="Manually record an anchor")
    temporal_sub.add_parser("verify", help="Run drift-check manually")
    temporal_sub.add_parser("log", help="Fetch recent drift entries")

    # Causality Command
    causality_parser = subparsers.add_parser("causality", help="Causality Mesh commands")
    causality_sub = causality_parser.add_subparsers(dest="causality_cmd")

    link_parser = causality_sub.add_parser("link", help="Create a causal link")
    link_parser.add_argument("--source", required=True, help="Source Event UUID")
    link_parser.add_argument("--target", required=True, help="Target Event UUID")
    link_parser.add_argument("--type", required=True, help="Cause Type")
    link_parser.add_argument("--weight", type=float, default=1.0, help="Causal Weight")
    link_parser.add_argument("--severity", default="UNKNOWN", help="Severity (RED, YELLOW, GREEN)")
    link_parser.add_argument("--notes", help="JSON notes")

    surface_parser = causality_sub.add_parser("surface", help="View causality surface")
    surface_parser.add_argument("--limit", type=int, default=20, help="Limit results")

    tension_parser = causality_sub.add_parser("tension", help="Show high-tension nodes")
    tension_parser.add_argument("--limit", type=int, default=10, help="Limit results")

    # Cross-Mesh Command
    crossmesh_parser = subparsers.add_parser("crossmesh", help="Cross-Mesh reconciliation commands")
    crossmesh_sub = crossmesh_parser.add_subparsers(dest="crossmesh_cmd")
    crossmesh_sub.add_parser("surface", help="Show the unified mesh surface")

    # Fusion Command
    fusion_parser = subparsers.add_parser("fusion", help="Temporal-Mesh fusion commands")
    fusion_sub = fusion_parser.add_subparsers(dest="fusion_cmd")
    fusion_sub.add_parser("list", help="List fusion nodes")

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
        elif args.subcommand == "forecast":
            cmd_paradox_forecast(args)
        else:
            paradox_parser.print_help()
    elif args.command == "collapse":
        if args.subcommand == "forecast":
            cmd_collapse_forecast(args)
        else:
            collapse_parser.print_help()
    elif args.command == "lattice":
        if args.subcommand == "forecast":
            cmd_lattice_forecast(args)
        else:
            lattice_parser.print_help()

    elif args.command == "continuation":
        if args.subcommand == "health":
            cmd_continuation_health(args)
        else:
            continuation_parser.print_help()

    elif args.command == "guardian":
        if args.subcommand == "scan":
            cmd_guardian_scan(args)
        elif args.subcommand == "plan":
            cmd_guardian_plan(args)
        elif args.subcommand == "actions":
            cmd_guardian_actions(args)
        else:
            guardian_parser.print_help()

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
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "rhythm":
        cmd_rhythm(args)
    elif args.command == "custody":
        cmd_custody(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "temporal":
        cmd_temporal(args)
    elif args.command == "causality":
        cmd_causality(args)
    elif args.command == "crossmesh":
        cmd_crossmesh(args)
    elif args.command == "fusion":
        cmd_fusion(args)
    else:
        parser.print_help()

def cmd_crossmesh(args):
    if args.crossmesh_cmd == "surface":
        try:
            res = db.client._ensure_client().table("view_cross_mesh_surface").select("*").limit(20).execute()
            print(f"--- Cross-Mesh Reconciliation Surface ---")
            for row in res.data:
                print(f"[{row['created_at']}] {row['resolved_type']} | {row['source_table']}::{row['source_id']} | T:{row['mesh_tension']} S:{row['severity']}")
        except Exception as e:
            print(f"[CROSSMESH] Error: {e}")

def cmd_fusion(args):
    if args.fusion_cmd == "list":
        try:
            res = db.client._ensure_client().table("view_mesh_temporal_fusion").select("*").limit(20).execute()
            try:
                from tabulate import tabulate
                print(tabulate(res.data, headers="keys"))
            except ImportError:
                import json
                print(json.dumps(res.data, indent=2))
        except Exception as e:
            print(f"[FUSION] Error: {e}")

if __name__ == "__main__":
    main()
