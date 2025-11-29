# scripts/run_guardian_sweep.py
import sys
import os
import time

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.guardian_actions import scan_future_lattice_window, plan_action_for_lattice

def run_sweep():
    print("🧹 [GUARDIAN SWEEP] Starting manual action planning sweep...")
    client = db.client._ensure_client()
    
    # Scan for all nodes in the last 24 hours (including stable)
    cutoff = (time.time() - 86400) # timestamp? No, Supabase expects ISO string
    from datetime import datetime, timedelta, timezone
    cutoff_iso = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    
    res = (
        client.table("view_future_lattice_surface")
        .select("*")
        .gte("created_at", cutoff_iso)
        .order("created_at", desc=True)
        .execute()
    )
    candidates = res.data or []
    
    if not candidates:
        print("✅ No actionable nodes found.")
        return

    print(f"🔹 Found {len(candidates)} candidates. Processing...")
    
    count = 0
    errors = 0
    
    for node in candidates:
        try:
            lattice_id = node['id']
            action_id = plan_action_for_lattice(client, lattice_id)
            if action_id:
                count += 1
                if count % 10 == 0:
                    print(f"   ... {count} actions planned")
        except Exception as e:
            print(f"❌ Failed to plan for {node['id']}: {e}")
            errors += 1
            
    print(f"✅ Sweep Complete. Planned {count} actions. Errors: {errors}")

if __name__ == "__main__":
    run_sweep()
