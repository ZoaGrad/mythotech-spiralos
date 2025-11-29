# scripts/verify_omega7_1.py
import sys
import os
import json

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.guardian_actions import plan_action_for_lattice, scan_future_lattice_window

def verify():
    print("🔹 [VERIFY] Checking imports...")
    try:
        import core.guardian_actions
        print("✅ core.guardian_actions imported")
    except ImportError as e:
        print(f"❌ Failed to import core.guardian_actions: {e}")
        return

    print("🔹 [VERIFY] Checking database connection...")
    try:
        client = db.client._ensure_client()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    print("🔹 [VERIFY] Checking schema objects...")
    try:
        # Check tables
        client.table("guardian_action_playbooks").select("id").limit(1).execute()
        print("✅ Table `guardian_action_playbooks` exists")
        
        client.table("guardian_action_events").select("id").limit(1).execute()
        print("✅ Table `guardian_action_events` exists")
        
        # Check seed data
        res = client.table("guardian_action_playbooks").select("count").execute()
        count = res.count
        if count and count >= 4:
             print(f"✅ Playbooks seeded (count: {count})")
        else:
             print(f"⚠️ Playbooks count low: {count}")

    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return

    print("🔹 [VERIFY] Smoke test: Guardian Planning...")
    try:
        # Find a lattice node to plan for
        # We need one that exists. If none, we can't test fully, but we can try scan.
        
        print("🔹 Scanning for candidates...")
        candidates = scan_future_lattice_window(client, window_minutes=1440) # Look back 24h
        
        if not candidates:
             # Try to just pick ANY lattice node
             res = client.table("integration_lattice").select("id").limit(1).execute()
             if res.data:
                 candidates = res.data
        
        if candidates:
            lattice_id = candidates[0]['id']
            print(f"🔹 Planning action for lattice {lattice_id}...")
            
            action_id = plan_action_for_lattice(client, lattice_id)
            
            if action_id:
                print(f"✅ Action planning successful. ID: {action_id}")
                
                # Verify in table
                act_res = client.table("guardian_action_events").select("*").eq("id", action_id).single().execute()
                if act_res.data:
                    print("✅ Action found in guardian_action_events")
                    row = act_res.data
                    print(f"   Action: {row['chosen_action']}")
                    print(f"   Severity: {row['severity']}")
                    print(f"   Status: {row['status']}")
                    
                    # Test Idempotency
                    print("🔹 Testing Idempotency...")
                    action_id_2 = plan_action_for_lattice(client, lattice_id)
                    if action_id == action_id_2:
                        print("✅ Idempotency verified (same ID returned)")
                    else:
                        print(f"❌ Idempotency failed: {action_id} != {action_id_2}")
                else:
                    print("❌ Action NOT found in table")
            else:
                print("❌ Plan action returned None")
        else:
            print("⚠️ No lattice nodes found to test planning.")

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
