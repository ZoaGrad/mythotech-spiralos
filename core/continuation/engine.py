# core/continuation/engine.py
from typing import Optional, Dict, Any
from core.db import db

def record_realization(
    future_chain_id: str,
    realized_state: str,
    realized_collapse: bool,
    notes: Optional[str] = None
) -> Optional[str]:
    """
    Records a realization for a FutureChain prediction.
    """
    try:
        resp = db.client._ensure_client().rpc(
            "fn_record_future_realization",
            {
                "p_future_chain_id": future_chain_id,
                "p_realized_state": realized_state,
                "p_realized_collapse": realized_collapse,
                "p_notes": notes
            }
        ).execute()
        
        if hasattr(resp, "data") and resp.data:
            return str(resp.data)
        return None
    except Exception as e:
        print(f"[CONTINUATION_FAIL] Chain {future_chain_id}: {e}")
        return None

def get_continuation_health_stats() -> Dict[str, Any]:
    """
    Fetches aggregated health stats from the view.
    """
    try:
        # We'll fetch the last 100 realized predictions
        res = (
            db.client._ensure_client()
            .table("view_continuation_health")
            .select("*")
            .not_.is_("realized_at", "null")
            .order("realized_at", desc=True)
            .limit(100)
            .execute()
        )
        
        data = res.data or []
        if not data:
            return {"count": 0, "avg_accuracy": 0, "trust_index": 0}
            
        total_acc = sum(float(row['accuracy_score']) for row in data)
        avg_acc = total_acc / len(data)
        
        # Trust Index: Weighted by recentness (simplified here as just avg accuracy for now)
        trust_index = avg_acc 
        
        return {
            "count": len(data),
            "avg_accuracy": avg_acc,
            "trust_index": trust_index,
            "recent_realizations": data[:5]
        }
    except Exception as e:
        print(f"[CONTINUATION_STATS_FAIL] {e}")
        return {}
