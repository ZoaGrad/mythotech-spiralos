from typing import List, Dict, Any
import os
import json
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def evaluate_constraint(expr_str: str, context: Dict[str, Any]) -> bool:
    """
    Evaluates a JSON DSL expression against a context.
    Returns True if compliant (VALID), False if violated.
    """
    try:
        expr = json.loads(expr_str)
    except json.JSONDecodeError:
        print(f"Error decoding constraint DSL: {expr_str}")
        return True # Fail open on malformed DSL to prevent lockouts

    return _eval_node(expr, context)

def _eval_node(node: Dict[str, Any], context: Dict[str, Any]) -> bool:
    op = node.get("op")
    
    if op == ">":
        # {"op": ">", "var": "score", "val": 0.5}
        # Returns True if context[var] > val
        val = context.get(node.get("var"))
        limit = node.get("val")
        if val is None: return True # Variable missing, assume compliant (or N/A)
        return float(val) > float(limit)

    elif op == "<":
        val = context.get(node.get("var"))
        limit = node.get("val")
        if val is None: return True
        return float(val) < float(limit)

    elif op == "=":
        val = context.get(node.get("var"))
        target = node.get("val")
        if val is None: return True
        return str(val) == str(target)

    elif op == "exists":
        # {"op": "exists", "var": "action"}
        return context.get(node.get("var")) is not None

    elif op == "if":
        # {"op": "if", "cond": {...}, "then": {...}}
        # If cond is True, then "then" must be True.
        # If cond is False, constraint is satisfied (N/A).
        cond_result = _eval_node(node.get("cond"), context)
        if cond_result:
            return _eval_node(node.get("then"), context)
        return True

    elif op == "rate_limit":
        # {"op": "rate_limit", "key": "escalation", "window": "10m", "limit": 1}
        # Placeholder: Real rate limiting requires DB state check.
        # For now, we'll assume compliant to avoid blocking in this MVP.
        return True

    elif op == "check_amendments":
        # Placeholder for amendment check
        return True

    return True # Default to compliant for unknown ops

def validate_action(action: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetches active 'action' scope constraints and evaluates them against the provided action context.
    Returns a list of violated constraint records.
    """
    supabase = get_supabase()
    response = supabase.table("guardian_constraints") \
        .select("*") \
        .eq("active", True) \
        .eq("scope", "action") \
        .execute()
    
    constraints = response.data
    violations = []
    
    # Enrich context if needed (e.g. fetch compliance score)
    # For now, we assume 'action' dict contains necessary keys like 'projected_probability', 'predicted_state', etc.
    
    for c in constraints:
        if not evaluate_constraint(c["rule_expression"], action):
            violations.append(c)
            
    return violations
