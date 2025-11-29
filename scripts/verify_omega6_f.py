# scripts/verify_omega6_f.py
import sys
import os
import json

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.paradox_predictor import project_collapse_from_paradox

def verify():
    print("🔹 [VERIFY] Checking imports...")
    try:
        import core.paradox_predictor
        print("✅ core.paradox_predictor imported")
    except ImportError as e:
        print(f"❌ Failed to import core.paradox_predictor: {e}")
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
        # Check table
        client.table("collapse_envelopes").select("id").limit(1).execute()
        print("✅ Table `collapse_envelopes` exists")
        
        # Check view
        client.table("view_collapse_horizon_surface").select("id").limit(1).execute()
        print("✅ View `view_collapse_horizon_surface` exists")
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return

    print("🔹 [VERIFY] Smoke test: Collapse Projection...")
    try:
        # Find a paradox map to project from
        # We need one that doesn't have a collapse envelope yet ideally, or just any
        res = client.table("predictive_paradox_maps").select("id").limit(1).execute()
        if not res.data:
            print("⚠️ No predictive_paradox_maps found. Skipping smoke test.")
        else:
            paradox_id = res.data[0]['id']
            print(f"🔹 Projecting collapse for paradox {paradox_id}...")
            
            collapse_id = project_collapse_from_paradox(
                paradox_id, 
                window_minutes=120,
                context={"source": "verify_omega6_f"}
            )
            
            if collapse_id:
                print(f"✅ Collapse projection successful. ID: {collapse_id}")
                
                # Verify in view
                view_res = client.table("view_collapse_horizon_surface").select("*").eq("id", collapse_id).single().execute()
                if view_res.data:
                    print("✅ Projection found in view_collapse_horizon_surface")
                    print(json.dumps(view_res.data, indent=2))
                else:
                    print("❌ Projection NOT found in view")
            else:
                print("❌ Collapse projection returned None (might be low risk or error)")

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
