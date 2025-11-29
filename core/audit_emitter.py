from .db import db

def emit_audit_event(event_type: str, component: str, payload: dict = None):
    """
    Emits an event to the Global Audit Surface.
    """
    if payload is None:
        payload = {}
    try:
        res = db.client._ensure_client().rpc("fn_emit_audit_surface_event", {
            "p_event_type": event_type,
            "p_component": component,
            "p_payload": payload
        }).execute()
        if res.data:
            return res.data
        return None
    except Exception as e:
        print(f"[AUDIT_EMIT_FAIL] {event_type} from {component}: {e}")
