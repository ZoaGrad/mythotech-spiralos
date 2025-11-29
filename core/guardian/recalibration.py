import os
import json
from typing import Optional, Dict, Any
from supabase import create_client, Client

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
supabase: Client = create_client(url, key)

def trigger_recalibration(window_hours: int = 24) -> Optional[str]:
    """
    Triggers the Guardian recalibration process via Supabase RPC.
    
    Args:
        window_hours: The lookback window in hours for recalibration.
        
    Returns:
        The UUID of the new recalibration log entry, or None if failed.
    """
    try:
        response = supabase.rpc(
            "fn_trigger_guardian_recalibration",
            {"p_window_hours": window_hours}
        ).execute()
        
        if response.data:
            return response.data
        return None
    except Exception as e:
        print(f"[GUARDIAN] Recalibration failed: {e}")
        return None

def assess_intervention_outcome(
    action_id: str,
    chain_id: str,
    actual_state: str,
    prevented_collapse: bool,
    notes: Optional[str] = None
) -> Optional[str]:
    """
    Assesses the outcome of a Guardian intervention.
    
    Args:
        action_id: UUID of the guardian action.
        chain_id: UUID of the future chain.
        actual_state: The actual state that occurred.
        prevented_collapse: Whether the intervention prevented a collapse.
        notes: Optional notes.
        
    Returns:
        The UUID of the new intervention outcome entry, or None if failed.
    """
    try:
        # Fetch the predicted state from the action
        action_response = supabase.table("guardian_action_events")\
            .select("lattice_state")\
            .eq("id", action_id)\
            .single()\
            .execute()
            
        if not action_response.data:
            print(f"[GUARDIAN] Action {action_id} not found for assessment.")
            return None
            
        predicted_state = action_response.data.get("lattice_state")
        
        # Compute effectiveness score
        effectiveness_score = 0.0
        if prevented_collapse:
            effectiveness_score = 1.0
        elif actual_state == predicted_state:
            effectiveness_score = 0.5
        else:
            effectiveness_score = 0.0
            
        # Insert outcome
        outcome_data = {
            "guardian_action_id": action_id,
            "future_chain_id": chain_id,
            "predicted_state": predicted_state,
            "actual_state": actual_state,
            "intervention_prevented_collapse": prevented_collapse,
            "effectiveness_score": effectiveness_score,
            "notes": notes
        }
        
        insert_response = supabase.table("intervention_outcomes")\
            .insert(outcome_data)\
            .execute()
            
        if insert_response.data:
            return insert_response.data[0].get("id")
        return None
        
    except Exception as e:
        print(f"[GUARDIAN] Intervention assessment failed: {e}")
        return None
