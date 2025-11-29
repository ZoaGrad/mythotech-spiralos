# scripts/verify_omega7.py
import sys
import os
import json

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.paradox_predictor import integrate_future_from_fusion

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
        client.table("integration_lattice").select("id").limit(1).execute()
        print("✅ Table `integration_lattice` exists")
        
        # Check view
        client.table("view_future_lattice_surface").select("id").limit(1).execute()
        print("✅ View `view_future_lattice_surface` exists")
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return

    print("🔹 [VERIFY] Smoke test: Future Integration...")
    try:
        # Find a fusion node to integrate
        res = client.table("mesh_temporal_fusion").select("id").limit(1).execute()
        if not res.data:
            print("⚠️ No mesh_temporal_fusion found. Skipping smoke test.")
        else:
            fusion_id = res.data[0]['id']
            print(f"🔹 Integrating future for fusion {fusion_id}...")
            
            lattice_id = integrate_future_from_fusion(fusion_id)
            
            if lattice_id:
                print(f"✅ Integration successful. ID: {lattice_id}")
                
                # Verify in view
                view_res = client.table("view_future_lattice_surface").select("*").eq("id", lattice_id).single().execute()
                if view_res.data:
                    print("✅ Projection found in view_future_lattice_surface")
                    row = view_res.data
                    print(f"   State: {row['lattice_state']}")
                    print(f"   Collapse Prob: {row['collapse_probability']}")
                    print(f"   Recommendation: {row['guardian_recommendation']}")
                else:
                    print("❌ Projection NOT found in view")
            else:
                print("❌ Integration returned None")

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
