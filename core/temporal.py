from datetime import datetime, timezone
from typing import Dict, Any
from .db import db

from .audit_emitter import emit_audit_event
from .causality_emitter import link_events

class TemporalDriftEngine:
    """
    Manages temporal coherence and drift detection.
    """
    def __init__(self):
        self.db = db

    def record_anchor(self, source: str = "System") -> str:
        """
        Records a temporal anchor point.
        """
        try:
            res = self.db.client._ensure_client().rpc("fn_record_temporal_anchor", {
                "p_source": source,
                "p_timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            anchor_id = res.data
            if anchor_id:
                emit_audit_event("temporal_anchor_recorded", "TemporalDriftEngine", {"anchor_id": anchor_id, "source": source})
            
            return anchor_id
        except Exception as e:
            print(f"[TEMPORAL] Anchor failed: {e}")
            return None

    def verify_drift(self, source: str = "System") -> Dict[str, Any]:
        """
        Verifies temporal drift against the server.
        """
        try:
            res = self.db.client._ensure_client().rpc("fn_verify_temporal_drift", {
                "p_client_timestamp": datetime.now(timezone.utc).isoformat(),
                "p_source": source
            }).execute()
            
            data = res.data
            # Emit verification event
            verify_event_id = emit_audit_event("temporal_drift_verified", "TemporalDriftEngine", data)
            
            # If RED, emit alert and link
            if data.get("severity") == "RED":
                alert_event_id = emit_audit_event("temporal_drift_alert", "TemporalDriftEngine", {"reason": "severity_red", "delta": data.get("delta_ms")})
                if verify_event_id and alert_event_id:
                    link_events(verify_event_id, alert_event_id, "temporal_severity_escalation", 1.0)
            
            return data
        except Exception as e:
            print(f"[TEMPORAL] Drift check failed: {e}")
            return {"error": str(e)}
