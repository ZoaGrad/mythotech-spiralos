import asyncio
import os
import inspect
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import Client, create_client

from core.guardian.anomaly_detector import AnomalyDetector
from core.audit_emitter import emit_audit_event
from core.temporal import TemporalDriftEngine
from core.causality_emitter import link_events
from core.guardian_actions import process_guardian_actions
from core.guardian.recalibration import trigger_recalibration

HEARTBEAT_FREQUENCY = 60


def initialize_supabase_client() -> Client | None:
    """Load credentials and initialize the Supabase client."""
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print(
            "[CRITICAL] Missing Supabase credentials; set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY in the environment."
        )
        return None

    try:
        return create_client(url, key)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[ACHE] Failed to initialize Supabase client: {exc}")
        return None


async def run_guardian_cycle() -> None:
    """Continuously run the Guardian anomaly detection heartbeat."""
    supabase_client = initialize_supabase_client()
    if supabase_client is None:
        return

    detector = AnomalyDetector(supabase_client)
    temporal = TemporalDriftEngine()
    print("[STATUS] Guardian Protocol vΩ.1 initialized.")

    while True:
        cycle_start = datetime.now(timezone.utc)
        print(f"[STATUS] Guardian heartbeat initiated at {cycle_start.isoformat()}")
        tick_id = emit_audit_event("guardian_tick", "GuardianRunner", {"timestamp": cycle_start.isoformat()})

        # Verify Drift
        drift_status = temporal.verify_drift(source="GuardianRunner")
        if drift_status.get("severity") == "RED":
            print(f"[TEMPORAL] CRITICAL DRIFT DETECTED: {drift_status.get('delta_ms')}ms")
            drift_event_id = emit_audit_event("drift_warning", "GuardianRunner", drift_status)
            if tick_id and drift_event_id:
                link_events(tick_id, drift_event_id, "temporal_drift_check", 0.9, {"severity": "RED"})

        try:
            anomalies = detector.detect_anomalies()
            if inspect.isawaitable(anomalies):
                anomalies = await anomalies

            if anomalies:
                for anomaly in anomalies:
                    print(f"[FRACTURE] {anomaly}")
                    # Emit anomaly event and link to tick
                    # Insert into guardian_anomalies
                    anomaly_payload = {
                        "anomaly_type": "COHERENCE_FRACTURE",
                        "severity": "HIGH",
                        "details": {"reason": anomaly.reason, "value": anomaly.value},
                        "detected_at": anomaly.created_at.isoformat(),
                        "status": "OPEN"
                    }
                    try:
                        res = supabase_client.table("guardian_anomalies").insert(anomaly_payload).execute()
                        if res.data:
                            anomaly_id = res.data[0]['id']
                            from core.cross_mesh import emit_cross_mesh
                            emit_cross_mesh("ANOMALY", "guardian_anomalies", anomaly_id, anomaly_payload)
                            
                            # Link to tick
                            if tick_id:
                                link_events(tick_id, anomaly_id, "guardian_anomaly_scan", 1.0)
                    except Exception as e:
                        print(f"[GUARDIAN] Failed to record anomaly: {e}")
            else:
                print("[FLOW] Coherence nominal; no anomalies detected.")
        except Exception as exc:  # pragma: no cover - resilience guard
            print(f"[ACHE] Anomaly detection issue: {exc}")

        # 4. Guardian-Action Layer (Ω.7.1)
        try:
            process_guardian_actions(supabase_client)
        except Exception as e:
            print(f"[GUARDIAN] Action processing error: {e}")

        # 5. Adaptive Recalibration (Ω.10)
        # Run every ~24 hours (1440 cycles at 60s heartbeat)
        # For simplicity, we'll use a modulo check on the current hour/minute or a simple counter if persistent
        # But since this is a loop, we can just check if it's time (e.g. once a day at a specific time or just interval)
        # Let's use a simple counter approach for now, initialized outside
        # actually, let's just run it if we haven't run it in the last 24h (would need state)
        # For this implementation, we'll just use a counter in memory.
        
        # We need to initialize the counter outside the loop, but for now let's just add it here
        # To avoid modifying the whole file structure too much, we'll use a static attribute or similar if possible
        # Or just rely on the fact that this runs in a loop.
        
        # Let's assume a global counter or similar.
        # Actually, let's just trigger it if the current hour is 0 and minute is 0 (midnight UTC)
        # This is a simple way to ensure it runs once a day.
        now_utc = datetime.now(timezone.utc)
        if now_utc.hour == 0 and now_utc.minute == 0:
             # To prevent multiple triggers in the same minute, we could check a flag or just let it be idempotent-ish
             # (it will run once per minute for that minute)
             # Better: check if we already ran it today.
             pass 
             # Actually, let's just call it every N cycles.
             
        # For robustness, let's just use a counter.
        if 'recalibration_counter' not in locals():
            recalibration_counter = 0
        
        recalibration_counter += 1
        if recalibration_counter >= 1440: # 24 hours * 60 minutes
            try:
                recal_id = trigger_recalibration()
                if recal_id:
                    print(f"[GUARDIAN] Recalibration triggered: {recal_id}")
                recalibration_counter = 0
            except Exception as e:
                print(f"[GUARDIAN] Recalibration error: {e}")

        elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()
        sleep_time = max(0, HEARTBEAT_FREQUENCY - elapsed)
        if sleep_time:
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(run_guardian_cycle())
