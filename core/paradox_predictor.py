# core/paradox_predictor.py
from typing import Any, Dict, Optional

from .db import db


def project_paradox_for_fusion(
    fusion_id: str,
    context: Optional[Dict[str, Any]] = None,
    window_minutes: int = 30,
) -> Optional[str]:
    client = db.client._ensure_client()
    payload = {
        "p_fusion_id": fusion_id,
        "p_window_minutes": window_minutes,
        "p_context": context or {},
    }

    resp = client.rpc("fn_project_paradox_from_fusion", payload).execute()
    if getattr(resp, "data", None):
        # Supabase RPC scalar return: data is the UUID
        paradox_id = resp.data
        
        # Check if we should project a collapse envelope
        # We need to fetch the paradox map to check risk
        try:
            p_res = client.table("predictive_paradox_maps").select("paradox_risk,risk_band").eq("id", paradox_id).single().execute()
            if p_res.data:
                risk = p_res.data.get("paradox_risk", 0)
                band = p_res.data.get("risk_band", "LOW")
                
                if risk >= 0.5 or band in ("HIGH", "CRITICAL"):
                    project_collapse_from_paradox(
                        paradox_id,
                        window_minutes=120,
                        context={
                            "trigger": "auto-collapse-envelope",
                            "source": "paradox_predictor",
                        }
                    )
        except Exception as e:
            print(f"[PARADOX] Failed to check/project collapse: {e}")

        return paradox_id
    return None


def project_collapse_from_paradox(
    paradox_map_id: str,
    window_minutes: int = 120,
    context: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Call fn_project_collapse_from_paradox and return the created collapse_envelope id.
    """
    client = db.client._ensure_client()
    payload = {
        "p_paradox_map_id": paradox_map_id,
        "p_window_minutes": window_minutes,
        "p_context": context or {},
    }

    try:
        resp = client.rpc("fn_project_collapse_from_paradox", payload).execute()
        if getattr(resp, "data", None):
            return resp.data
    except Exception as e:
        print(f"[COLLAPSE] Projection failed for paradox {paradox_map_id}: {e}")
    
    return None
