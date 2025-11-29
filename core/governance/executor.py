import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from core.db import db
from core.governance.validators import validate_action

def enforce_constitution(action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Apply constitutional constraints to a proposed action.
    Returns:
      - None: if action is VETOED
      - Dict: if action is ALLOWED (potentially rewritten)
    """
    client = db.client._ensure_client()
    
    # 1. Validate against active constraints
    violations = validate_action(action)
    
    if not violations:
        # Compliant - Log execution and return
        _log_execution(client, action, executed=True, vetoed=False, rewritten=False, violations=[])
        return action

    # 2. Handle Violations (Veto or Rewrite)
    # For now, we'll assume most violations are VETO unless we have specific rewrite logic.
    # We can implement a simple rewrite rule: 
    # If violation is C-02 (Escalation w/o threshold), rewrite to "stabilize" if possible.
    
    rewritten_action = None
    rewrite_reason = ""
    applied_rewrite_constraint = ""
    
    for v in violations:
        # C-01: Proportional Response (Prob > 0.5)
        if v['constraint_code'] == 'C-01' and action.get('chosen_action') == 'escalate':
            # If prob is decent (e.g. > 0.3), rewrite to stabilize.
            # If prob is very low (< 0.3), let it be vetoed.
            if action.get('projected_probability', 0) > 0.3:
                rewritten_action = action.copy()
                rewritten_action['chosen_action'] = 'stabilize'
                rewritten_action['severity'] = 'low'
                rewrite_reason = "Downgraded escalation to stabilization (C-01: Prob too low for escalation but > 0.3)."
                applied_rewrite_constraint = "C-01"
                break

        # C-02: No Silent Catastrophe (If Critical, Must Act)
        # If violated, it means chosen_action is missing or invalid.
        if v['constraint_code'] == 'C-02':
             # Force an action
             rewritten_action = action.copy()
             rewritten_action['chosen_action'] = 'stabilize'
             rewritten_action['severity'] = 'high'
             rewrite_reason = "Forced action due to critical state (C-02)."
             applied_rewrite_constraint = "C-02"
             break
            
    if rewritten_action:
        # Log the rewrite
        try:
            client.table("action_rewrites").insert({
                "original_action": action,
                "rewritten_action": rewritten_action,
                "reason": rewrite_reason,
                "constraint_id": applied_rewrite_constraint
            }).execute()
        except Exception as e:
            print(f"[EXECUTOR] Failed to log rewrite: {e}")

        # Log execution of rewritten action
        _log_execution(client, rewritten_action, executed=True, vetoed=False, rewritten=True, violations=violations, notes=rewrite_reason)
        return rewritten_action

    # 3. Veto (Default if not rewritten)
    _log_execution(client, action, executed=False, vetoed=True, rewritten=False, violations=violations, notes="Action vetoed due to constitutional violations.")
    return None

def wrap_guardian_action(proposed_action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Wrapper for Guardian actions to enforce constitution.
    """
    print(f"[EXECUTOR] Enforcing constitution on action {proposed_action.get('id')}...")
    return enforce_constitution(proposed_action)

def _log_execution(client, action, executed, vetoed, rewritten, violations, notes=""):
    try:
        client.table("constitutional_execution_log").insert({
            "action_id": action.get("id"),
            "executed": executed,
            "vetoed": vetoed,
            "rewritten": rewritten,
            "validation_path": json.dumps([v['constraint_code'] for v in violations]), # Simplified path
            "applied_constraints": json.dumps(violations),
            "notes": notes
        }).execute()
    except Exception as e:
        print(f"[EXECUTOR] Failed to log execution: {e}")
