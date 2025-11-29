# core/paradox_predictor.py
from typing import Any, Dict, Optional

from .db import get_client


def project_paradox_for_fusion(
    fusion_id: str,
    context: Optional[Dict[str, Any]] = None,
    window_minutes: int = 30,
) -> Optional[str]:
    client = get_client()
    payload = {
        "p_fusion_id": fusion_id,
        "p_window_minutes": window_minutes,
        "p_context": context or {},
    }

    resp = client.rpc("fn_project_paradox_from_fusion", payload).execute()
    if getattr(resp, "data", None):
        # Supabase RPC scalar return: data is the UUID
        return resp.data
    return None
