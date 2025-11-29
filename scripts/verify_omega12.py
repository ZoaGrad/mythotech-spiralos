import sys
import os
import json
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from supabase import create_client
from core.governance.executor import enforce_constitution

def verify_omega12():
    print("🔹 [VERIFY] Sequence Ω.12: Constitutional Execution Engine")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)
    
    # 1. Verify Database Objects
    print("\n1. Verifying Database Objects...")
    tables = ["action_rewrites", "constitutional_execution_log"]
    all_tables_exist = True
    
    for table in tables:
        try:
            supabase.table(table).select("id").limit(1).execute()
            print(f"  ✅ Table '{table}' exists")
        except Exception as e:
            print(f"  ❌ Table '{table}' check failed: {e}")
            all_tables_exist = False
            
    if not all_tables_exist:
        print("❌ Database verification failed.")
        return False

    # 2. Test Enforcement Logic (Veto)
    print("\n2. Testing Enforcement Logic (Veto)...")
    # Action violating C-01 (Escalate with low prob < 0.3) -> Should Veto
    veto_action = {
        "id": str(uuid.uuid4()),
        "projected_probability": 0.1,
        "predicted_state": "stable",
        "chosen_action": "escalate", 
        "severity": "high"
    }
    
    print(f"  Testing Veto Action: {veto_action['id']}")
    result = enforce_constitution(veto_action)
    
    if result is None:
        print("  ✅ Action VETOED correctly.")
    else:
        print(f"  ❌ Action NOT vetoed (Result: {result})")

    # 3. Test Enforcement Logic (Rewrite)
    print("\n3. Testing Enforcement Logic (Rewrite)...")
    # Action violating C-01 (Escalate with prob 0.4 > 0.3) -> Should Rewrite to Stabilize
    rewrite_action = {
        "id": str(uuid.uuid4()),
        "projected_probability": 0.4, 
        "predicted_state": "stable",
        "chosen_action": "escalate",
        "severity": "high"
    }
    
    print(f"  Testing Rewrite Action: {rewrite_action['id']}")
    
    result = enforce_constitution(rewrite_action)
    
    if result and result != rewrite_action:
        print("  ✅ Action REWRITTEN.")
        if result['chosen_action'] == 'stabilize':
             print("  ✅ Rewritten to 'stabilize' as expected.")
        else:
             print(f"  ⚠️ Rewritten to unexpected value: {result['chosen_action']}")
    elif result is None:
        print("  ⚠️ Action VETOED instead of rewritten (Check executor logic).")
    else:
        print("  ❌ Action ALLOWED unchanged (Should have been rewritten).")

    # 4. Test Compliant Action
    print("\n4. Testing Compliant Action...")
    # Compliant with C-01 (Prob > 0.5) and C-02 (Has chosen_action)
    compliant_action = {
        "id": str(uuid.uuid4()),
        "projected_probability": 0.8,
        "predicted_state": "critical",
        "chosen_action": "escalate",
        "severity": "high"
    }
    
    print(f"  Testing Compliant Action: {compliant_action['id']}")
    result = enforce_constitution(compliant_action)
    
    if result == compliant_action:
        print("  ✅ Action ALLOWED unchanged.")
    else:
        print(f"  ❌ Action modified or vetoed unexpectedly (Result: {result})")

    print("\n✅ Sequence Ω.12 Verification Complete.")
    return True

if __name__ == "__main__":
    verify_omega12()
