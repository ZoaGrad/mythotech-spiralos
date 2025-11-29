# scripts/simulate_realizations_omega9.py
import sys
import os
import time
import json
import random

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.continuation.engine import record_realization, get_continuation_health_stats

def run_simulation(count=100):
    print(f"🎲 [Ω.9] Starting Realization Simulation ({count} events)...")
    client = db.client._ensure_client()
    
    # 1. Fetch pending chain nodes (those without realizations)
    # Since we can't easily do a "NOT IN" join via simple client, we'll fetch recent chain nodes
    # and just assume we can realize them. The DB table allows multiple realizations per chain node?
    # No, usually 1:1. But we didn't add a unique constraint in the migration (oops/feature).
    # Let's just fetch recent ones.
    
    res = client.table("future_chain").select("*").order("created_at", desc=True).limit(count).execute()
    nodes = res.data or []
    
    if not nodes:
        print("⚠️ No FutureChain nodes found. Run Ω.8 load test first.")
        return

    print(f"   Found {len(nodes)} chain nodes to realize.")
    
    realized_count = 0
    
    for node in nodes:
        try:
            # Simulate outcome based on probability
            # If predicted prob is high, it likely collapsed.
            # If Guardian intervened (stabilize), it likely didn't collapse.
            
            prob = float(node['projected_state']['projected_probability'])
            influence = node['guardian_influence']
            
            # Bias the dice roll
            if influence == 'stabilize':
                prob *= 0.2 # Guardian worked
            elif influence == 'escalate':
                prob *= 0.5 # Guardian tried
                
            is_collapse = random.random() < prob
            state = "collapsed" if is_collapse else "stable"
            
            record_realization(
                future_chain_id=node['id'],
                realized_state=state,
                realized_collapse=is_collapse,
                notes="Simulation Ω.9"
            )
            realized_count += 1
            
            if realized_count % 10 == 0:
                print(f"   ... realized {realized_count} outcomes")
                
        except Exception as e:
            print(f"❌ Failed to realize {node['id']}: {e}")
            
    # Report
    stats = get_continuation_health_stats()
    print("\n📊 [Ω.9 REPORT]")
    print(json.dumps(stats, indent=2))
    print(f"✅ Simulation Complete. Realized {realized_count} events.")

if __name__ == "__main__":
    run_simulation(100)
