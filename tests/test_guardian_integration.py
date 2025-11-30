import os
import time
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db import get_supabase

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def test_guardian_integration():
    """
    Verify Guardianship Integration:
    1. Check guardian_configs access.
    2. Log a heartbeat to guardian_logs.
    3. Simulate a witness entry.
    """
    print("🛡️ Starting Guardian Integration Verification...")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Missing Supabase credentials. Skipping real integration test.")
        return

    try:
        supabase = get_supabase()
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        return
    
    # 1. Check guardian_configs
    # Try to insert a test config
    config_key = f"test_config_{int(time.time())}"
    config_data = {"test": "value"}
    
    try:
        res = supabase.table("guardian_configs").insert({
            "key": config_key,
            "value": config_data,
            "description": "Integration test config"
        }).execute()
        
        if not res.data:
            raise Exception("No data returned from insert")
            
        print(f"✅ Inserted test config: {config_key}")
        
        # Clean up
        supabase.table("guardian_configs").delete().eq("key", config_key).execute()
        print("✅ Cleaned up test config.")
        
    except Exception as e:
        print(f"❌ Failed to access guardian_configs: {e}")
        # Don't return, try other steps

    # 2. Log Heartbeat
    try:
        log_entry = {
            "agent_id": "test_guardian_integration",
            "action": "heartbeat",
            "target": "system",
            "result": "success",
            "details": {"test": True}
        }
        res = supabase.table("guardian_logs").insert(log_entry).execute()
        if res.data:
            print("✅ Logged heartbeat to guardian_logs.")
        else:
            print("⚠️ Logged heartbeat but no data returned.")
    except Exception as e:
        print(f"❌ Failed to log heartbeat: {e}")

    # 3. Simulate Witness Entry
    try:
        witness_entry = {
            "witness_id": "test_witness_user",
            "entry_data": {"narrative": "Test witness entry from integration script"},
            "status": "pending"
        }
        res = supabase.table("witness_entries").insert(witness_entry).execute()
        if res.data:
            print("✅ Inserted witness entry.")
            # Optional: Clean up witness entry? 
            # Maybe leave it for manual inspection or delete it.
            # Let's delete it to keep clean.
            entry_id = res.data[0]['id']
            supabase.table("witness_entries").delete().eq("id", entry_id).execute()
            print("✅ Cleaned up witness entry.")
        else:
             print("⚠️ Inserted witness entry but no data returned.")

    except Exception as e:
        print(f"❌ Failed to insert witness entry: {e}")

    print("🛡️ Guardianship Integration Verification Complete.")

if __name__ == "__main__":
    test_guardian_integration()
