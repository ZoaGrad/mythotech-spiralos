from typing import Dict, Any, Optional
import os
from supabase import create_client, Client
from core.governance.validators import validate_action

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def enforce_governance(action: Dict[str, Any]) -> bool:
    """
    Validates a Guardian action against constitutional constraints.
    If violations occur, records them and returns False (VETO).
    If no violations, returns True (ALLOW).
    """
    violations = validate_action(action)
    
    if not violations:
        return True
        
    supabase = get_supabase()
    
    for v in violations:
        print(f"🚫 [GOVERNANCE] VETO: Action violates {v['constraint_code']} - {v['description']}")
        
        # Record violation
        supabase.rpc("fn_record_constraint_violation", {
            "p_constraint_code": v["constraint_code"],
            "p_action_id": action.get("id"), # Might be None if action not yet created
            "p_severity": "error", # Default to error for vetoed actions
            "p_notes": f"Vetoed by enforce_governance. Rule: {v['rule_expression']}"
        }).execute()
        
    return False
