from core.db import db

def emit_cross_mesh(event_type: str, table: str, source_id: str, payload: dict = None):
    """
    Emits an event to the Cross-Mesh Reconciliation Surface.
    """
    payload = payload or {}
    try:
        db.client._ensure_client().rpc(
            "fn_emit_cross_mesh_event",
            {
                "p_event_type": event_type,
                "p_source_table": table,
                "p_source_id": source_id,
                "p_payload": payload,
            }
        ).execute()
    except Exception as e:
        print(f"[CROSS_MESH_EMIT_FAIL] {event_type}: {e}")
