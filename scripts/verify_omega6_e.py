# scripts/verify_omega6_e.py
import sys
import os
import json

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.paradox_predictor import project_paradox_for_fusion

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

    print("🔹 [VERIFY] Checking for fusion nodes...")
    try:
        res = client.table("mesh_temporal_fusion").select("id").limit(1).execute()
        fusion_nodes = res.data
        if not fusion_nodes:
            print("⚠️ No fusion nodes found. Cannot test projection execution.")
        else:
            fusion_id = fusion_nodes[0]['id']
            print(f"✅ Found fusion node: {fusion_id}")
            
            print(f"🔹 [VERIFY] Attempting paradox projection for {fusion_id}...")
            paradox_id = project_paradox_for_fusion(fusion_id, {"source": "verification_script"})
            
            if paradox_id:
                print(f"✅ Paradox projection successful. ID: {paradox_id}")
                
                # Verify it appears in the view
                print("🔹 [VERIFY] Checking view_paradox_risk_surface...")
                view_res = client.table("view_paradox_risk_surface").select("*").eq("id", paradox_id).execute()
                if view_res.data:
                    print("✅ Projection found in view_paradox_risk_surface")
                    print(json.dumps(view_res.data[0], indent=2))
                else:
                    print("❌ Projection NOT found in view (might be a delay or RLS issue)")
            else:
                print("❌ Paradox projection returned None")

    except Exception as e:
        print(f"❌ Runtime verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
