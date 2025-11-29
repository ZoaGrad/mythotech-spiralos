from .db import db
from typing import Optional, Dict, Any

def link_events(
    source_event_id: str,
    target_event_id: str,
    cause_type: str,
    weight: float = 1.0,
    notes: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Emit a causal link between two audit_surface_events.

    Returns the new causal_event_links.id or None on failure.
    """
    if notes is None:
        notes = {}
        
    try:
        resp = db.client._ensure_client().rpc(
            "fn_link_events",
            {
                "p_source_event_id": source_event_id,
                "p_target_event_id": target_event_id,
                "p_cause_type": cause_type,
                "p_weight": weight,
                "p_notes": notes,
            },
        ).execute()

        if hasattr(resp, "data") and resp.data:
            return str(resp.data)
        return None
    except Exception as e:
        print(f"[CAUSALITY_LINK_FAIL] {source_event_id} -> {target_event_id}: {e}")
        return None
