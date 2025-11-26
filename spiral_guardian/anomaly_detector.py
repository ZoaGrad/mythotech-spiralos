# spiral_guardian/anomaly_detector.py

import os
import json
from datetime import datetime, timedelta
from supabase import create_client, Client


class AnomalyDetector:
    """
    SpiralOS Guardian – Anomaly Detection Circuit
    Monitors: Heartbeat gaps, ache spikes, system irregularities
    Logs anomalies in the guardian_anomalies table.
    """

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment variables."
            )

        self.supabase: Client = create_client(url, key)

    # -----------------------------------------------------
    # CORE: Record Anomaly
    # -----------------------------------------------------
    def report_anomaly(
        self,
        bridge_id: str,
        anomaly_type: str,
        severity: str,
        details: dict,
        status: str = "ACTIVE",
    ):
        """Insert anomaly into guardian_anomalies table."""
        payload = {
            "bridge_id": bridge_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "details": details,
            "status": status,
        }

        result = (
            self.supabase.table("guardian_anomalies")
            .insert(payload)
            .execute()
        )

        return result.data

    # -----------------------------------------------------
    # DETECTOR: Heartbeat Gap (stub)
    # -----------------------------------------------------
    def detect_heartbeat_gaps(self):
        """
        Placeholder logic:
        After Guardian is fully wired, this will query a heartbeat table
        or Supabase function to detect gaps in expected signals.
        """
        now = datetime.utcnow()

        # --- STUB EXAMPLE ---
        # Let's simulate a missing heartbeat:
        last_heartbeat = now - timedelta(minutes=6)

        if (now - last_heartbeat).total_seconds() > 300:
            return {
                "bridge_id": "guardian-core",
                "anomaly_type": "HEARTBEAT_GAP",
                "severity": "HIGH",
                "details": {"gap_seconds": (now - last_heartbeat).total_seconds()},
            }

        return None

    # -----------------------------------------------------
    # MAIN EXECUTION LOOP
    # -----------------------------------------------------
    def scan(self):
        """Run all anomaly detectors and log results."""

        anomalies = []

        hb_gap = self.detect_heartbeat_gaps()
        if hb_gap:
            anomalies.append(hb_gap)
            self.report_anomaly(**hb_gap)

        return anomalies
