# core/guardian_actions.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from .db import db

def scan_future_lattice_window(
    client=None,
    window_minutes: int = 30,
    min_severity: int = 1, # Not strictly used in query yet, but good for API signature
) -> List[Dict[str, Any]]:
    """
    Pull high-risk/strained/critical lattice nodes from view_future_lattice_surface
    within the last `window_minutes`.
    """
    if not client:
        client = db.client._ensure_client()
        
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_minutes)).isoformat()
    
    # We want nodes created recently that are NOT stable (strained, critical, collapsed)
    # OR have high collapse probability.
    # For efficiency, let's just query the view.
    
    try:
        res = (
            client.table("view_future_lattice_surface")
            .select("*")
            .gte("created_at", cutoff)
            .neq("lattice_state", "stable") # Only actionable states
            .order("collapse_probability", desc=True)
            .execute()
        )
        return res.data or []
    except Exception as e:
        print(f"[GUARDIAN] Scan failed: {e}")
        return []

def plan_action_for_lattice(client, lattice_id: str) -> Optional[str]:
    """
    Calls fn_guardian_plan_for_lattice and returns guardian_action_events.id.
    """
    if not client:
        client = db.client._ensure_client()
        
    try:
        resp = client.rpc("fn_guardian_plan_for_lattice", {"p_lattice_id": lattice_id}).execute()
        if getattr(resp, "data", None):
            return resp.data
    except Exception as e:
        print(f"[GUARDIAN] Plan action failed for lattice {lattice_id}: {e}")
    
    return None

def process_guardian_actions(client=None) -> None:
    """
    Main orchestration:
      - Scan lattice.
      - For each candidate, call plan_action_for_lattice.
      - Optionally emit logs or notifications for actions with severity >= threshold.
    """
    if not client:
        client = db.client._ensure_client()
        
    print("[GUARDIAN] Scanning future lattice for actionable nodes...")
    candidates = scan_future_lattice_window(client, window_minutes=60)
    
    if not candidates:
        print("[GUARDIAN] No actionable lattice nodes found.")
        return

    print(f"[GUARDIAN] Found {len(candidates)} candidates.")
    
    for node in candidates:
        lattice_id = node.get("id")
        state = node.get("lattice_state")
        prob = node.get("collapse_probability")
        
        print(f" -> Processing {lattice_id} [{state} | {prob}]")
        
        action_id = plan_action_for_lattice(client, lattice_id)
        
        if action_id:
            # Fetch the action to log it
            try:
                act_res = client.table("guardian_action_events").select("chosen_action,severity").eq("id", action_id).single().execute()
                if act_res.data:
                    act = act_res.data
                    print(f"    [ACTION] {act['chosen_action']} (Sev: {act['severity']}) -> {action_id}")
            except Exception:
                pass
