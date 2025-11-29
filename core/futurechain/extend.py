# core/futurechain/extend.py
from typing import Optional
from core.db import db

def extend_chain_from_lattice(lattice_id: str) -> Optional[str]:
    """
    Calls the Supabase RPC to extend the FutureChain from a given lattice node.
    Returns the new future_chain.id or None on failure.
    """
    try:
        resp = db.client._ensure_client().rpc(
            "fn_extend_future_chain",
            {"p_lattice_id": lattice_id}
        ).execute()
        
        if hasattr(resp, "data") and resp.data:
            return str(resp.data)
        return None
    except Exception as e:
        print(f"[FUTURECHAIN_EXTEND_FAIL] Lattice {lattice_id}: {e}")
        return None
