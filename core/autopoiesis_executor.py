# ========================================================
# Sequence J₀ — Autopoiesis Executor
# ========================================================

from core.db import db
from core.coherence import CoherenceEngine


class AutopoiesisExecutor:
    """
    Applies approved changes and manages rollback using snapshots.
    """

    def __init__(self, coherence: CoherenceEngine):
        self.coherence = coherence

    def execute_change(self, change_request_id: str):
        req = db.fetch_change_request(change_request_id)
        if req["status"] != "approved":
            raise ValueError(f"Change {change_request_id} not approved.")

        db.capture_structure_snapshot(req, "pre")
        db.apply_sql_diff(req["sql_diff"])
        db.capture_structure_snapshot(req, "post")

        db.mark_change_executed(change_request_id)
        
        # Check if current_score_delta exists, otherwise use a placeholder
        if hasattr(self.coherence, 'current_score_delta'):
            delta_c = self.coherence.current_score_delta()
        else:
            delta_c = 0.0

        db.log_structural_execution(change_request_id, delta_c)

        return {
            "change_request_id": change_request_id,
            "coherence_delta": delta_c,
        }

    def rollback_change(self, change_request_id: str):
        snapshot = db.fetch_snapshot(change_request_id, "pre")
        if not snapshot:
            raise RuntimeError("No pre-snapshot available.")

        reverse_ddl = db.generate_reverse_ddl(snapshot)
        db.apply_sql_diff(reverse_ddl)

        db.mark_change_rolled_back(change_request_id)
        return {"rolled_back": True}
