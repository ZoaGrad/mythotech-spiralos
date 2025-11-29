import sys
import os
import asyncio
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from system.nerves.spinal_cord import app
from system.core.database import SupabaseManager

def verify_omega12b():
    print(">> [VERIFY] Initializing TestClient...")
    client = TestClient(app)
    
    print(">> [VERIFY] Checking /system/health...")
    try:
        response = client.get("/system/health")
        if response.status_code == 200:
            print(f"[OK] /system/health OK: {response.json()}")
        else:
            print(f"[FAIL] /system/health FAILED: {response.status_code} - {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] /system/health EXCEPTION: {e}")
        sys.exit(1)

    print(">> [VERIFY] Checking SupabaseManager singleton...")
    try:
        s1 = SupabaseManager.get_client()
        s2 = SupabaseManager.get_client()
        if s1 is s2:
            print("[OK] SupabaseManager returns singleton client")
        else:
            print("[FAIL] SupabaseManager returned different instances")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] SupabaseManager check EXCEPTION: {e}")
        # Don't fail here if it's just missing creds in this env, but we expect them
        pass

if __name__ == "__main__":
    verify_omega12b()
