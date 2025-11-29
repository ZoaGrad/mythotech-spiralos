import sys
import os
import json
import uuid
import random
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.governance.executor import enforce_constitution

def load_test_omega12():
    print("🔹 [LOAD TEST] Sequence Ω.12: Constitutional Execution Engine")
    print("Generating 1000 simulated actions...")
    
    actions = []
    for _ in range(1000):
        # Mix of compliant, vetoable, and rewritable actions
        r = random.random()
        if r < 0.1:
            # Vetoable (Low prob escalation)
            act = {
                "id": str(uuid.uuid4()),
                "projected_probability": 0.1,
                "predicted_state": "stable",
                "chosen_action": "escalate",
                "severity": "high"
            }
        elif r < 0.2:
            # Rewritable (Stable state escalation)
            act = {
                "id": str(uuid.uuid4()),
                "projected_probability": 0.6,
                "predicted_state": "stable",
                "chosen_action": "escalate",
                "severity": "high"
            }
        else:
            # Compliant
            act = {
                "id": str(uuid.uuid4()),
                "projected_probability": 0.8,
                "predicted_state": "critical",
                "chosen_action": "stabilize",
                "severity": "medium"
            }
        actions.append(act)
        
    print("Starting execution...")
    start_time = time.time()
    
    vetoed = 0
    rewritten = 0
    executed = 0
    
    for i, action in enumerate(actions):
        if i % 100 == 0:
            print(f"  Processed {i}/1000 actions...")
            
        result = enforce_constitution(action)
        
        if result is None:
            vetoed += 1
        elif result != action:
            rewritten += 1
        else:
            executed += 1
            
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n--- Load Test Results ---")
    print(f"Total Actions: 1000")
    print(f"Time Taken: {duration:.2f}s ({1000/duration:.2f} actions/s)")
    print(f"Vetoed: {vetoed}")
    print(f"Rewritten: {rewritten}")
    print(f"Executed (Unchanged): {executed}")
    
    # Basic assertions
    if vetoed > 0 and rewritten > 0 and executed > 0:
        print("✅ Traffic mix verified (Vetoes, Rewrites, and Executions occurred).")
    else:
        print("⚠️ Warning: Traffic mix not fully representative.")
        
    print("✅ Load Test Complete.")

if __name__ == "__main__":
    load_test_omega12()
