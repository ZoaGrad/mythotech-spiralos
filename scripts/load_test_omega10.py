import sys
import os
import time
import random
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from supabase import create_client
from core.guardian.recalibration import trigger_recalibration

def load_test_omega10():
    print("🔹 [LOAD TEST] Sequence Ω.10: Adaptive Recalibration Stress Test")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase = create_client(url, key)
    
    # 1. Generate Synthetic Realizations
    print("1. Generating synthetic future_chain_realizations...")
    # We need to insert into future_chain_realizations.
    # This table likely requires future_chain_id.
    # We'll try to use existing future_chain rows or create dummy ones.
    
    chains = supabase.table("future_chain").select("id").limit(50).execute()
    chain_ids = [c['id'] for c in chains.data]
    
    if not chain_ids:
        print("  ⚠️ No future chains found. Skipping data generation.")
    else:
        realizations = []
        for i in range(20): # Generate 20 realizations
            chain_id = random.choice(chain_ids)
            accuracy = random.uniform(0.5, 1.0)
            realizations.append({
                "future_chain_id": chain_id,
                "realized_state": "STABLE",
                "realized_collapse": False,
                "accuracy_score": accuracy,
                "notes": "Synthetic Load Test",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
        try:
            supabase.table("future_chain_realizations").insert(realizations).execute()
            print(f"  ✅ Inserted {len(realizations)} synthetic realizations.")
        except Exception as e:
            print(f"  ❌ Failed to insert realizations: {e}")

    # 2. Run Recalibration Cycles
    print("\n2. Running Recalibration Cycles...")
    for i in range(3):
        print(f"  Cycle {i+1}/3...")
        try:
            log_id = trigger_recalibration(window_hours=24)
            if log_id:
                # Fetch result
                log = supabase.table("guardian_recalibration_log").select("new_trust_index,calibration_error").eq("id", log_id).single().execute()
                print(f"    ✅ Recalibrated. New Trust Index: {log.data['new_trust_index']:.4f}, Error: {log.data['calibration_error']:.4f}")
            else:
                print("    ❌ Recalibration failed (None returned)")
        except Exception as e:
            print(f"    ❌ Recalibration error: {e}")
        
        time.sleep(1)

    print("\n✅ Load Test Complete.")

if __name__ == "__main__":
    load_test_omega10()
