import asyncio
import os
import inspect
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import Client, create_client

from core.guardian.anomaly_detector import AnomalyDetector
from core.audit_emitter import emit_audit_event
from core.temporal import TemporalDriftEngine
from core.causality_emitter import link_events

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
                    anomaly_event_id = emit_audit_event("anomaly_detected", "GuardianRunner", {"anomaly": str(anomaly)})
                    if tick_id and anomaly_event_id:
                        link_events(tick_id, anomaly_event_id, "guardian_anomaly_scan", 1.0)
            else:
                print("[FLOW] Coherence nominal; no anomalies detected.")
        except Exception as exc:  # pragma: no cover - resilience guard
            print(f"[ACHE] Anomaly detection issue: {exc}")

        elapsed = (datetime.now(timezone.utc) - cycle_start).total_seconds()
        sleep_time = max(0, HEARTBEAT_FREQUENCY - elapsed)
        if sleep_time:
            await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(run_guardian_cycle())
