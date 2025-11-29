
from .db import db
from typing import Optional, Dict, Any

def link_events(
    source_event_id: str,
    target_event_id: str,
    cause_type: str,
    severity: str = "UNKNOWN",
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
        # 1. Create Link
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

        link_id = None
        if hasattr(resp, "data") and resp.data:
            link_id = str(resp.data)
        
        # 2. Update Metrics (Severity, Normalized Weight, Tension)
        if link_id:
            db.client._ensure_client().rpc(
                "fn_update_causality_metrics",
                {
                    "p_link_id": link_id,
                    "p_severity": severity,
                    "p_weight": weight
                }
            ).execute()
            
            from core.cross_mesh import emit_cross_mesh
            emit_cross_mesh("CAUSAL_LINK", "causal_event_links", link_id, notes)

            # 3. Temporal Fusion (Ω.6-D)
            fuse_temporal_mesh(link_id, {"trigger": "auto-fusion", "notes": notes})

        return link_id
    except Exception as e:
        print(f"[CAUSALITY_LINK_FAIL] {source_event_id} -> {target_event_id}: {e}")
        return None

def fuse_temporal_mesh(link_id: str, context: Optional[Dict[str, Any]] = None):
    context = context or {}
    try:
        db.client._ensure_client().rpc(
            "fn_fuse_mesh_temporal",
            {
                "p_causal_link_id": link_id,
                "p_context": context
            }
        ).execute()
    except Exception as e:
        print(f"[FUSION_FAIL] {link_id}: {e}")
