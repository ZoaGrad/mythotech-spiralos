import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db

def main():
    print("[TEST] Calling fn_status_api RPC...")
    try:
        res = db.client._ensure_client().rpc("fn_status_api", {}).execute()
        print("[TEST] Response:")
        print(json.dumps(res.data, indent=2))
        
        if res.data and "lock_status" in res.data:
            print("[TEST] SUCCESS: Status API returned valid structure.")
        else:
            print("[TEST] FAILURE: Unexpected response structure.")
            
    except Exception as e:
        print(f"[TEST] ERROR: {e}")

if __name__ == "__main__":
    main()
