from .db import db
from .audit_emitter import emit_audit_event

class PhaseLockEngine:
    def verify(self):
        """
        Verifies the system phase lock integrity.
        """
        try:
            res = db.client._ensure_client().rpc("fn_verify_phase_lock", {}).execute()
            result = res.data
            
            emit_audit_event("phase_lock_verify", "PhaseLockEngine", {
                "valid": result.get("valid", False),
                "hash": result.get("hash")
            })
            return result
        except Exception as e:
            emit_audit_event("phase_lock_verify_error", "PhaseLockEngine", {"error": str(e)})
            raise e
