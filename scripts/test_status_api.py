import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.status_api import StatusAPI

def main():
    print("[TEST] Initializing StatusAPI...")
    api = StatusAPI(db)
    
    print("[TEST] Calling get_status()...")
    data = api.get_status()
    
    print("[TEST] Response:")
    print(json.dumps(data, indent=2))
    
    if data and "lock_status" in data:
        print("[TEST] SUCCESS: Status API returned valid structure.")
    else:
        print("[TEST] FAILURE: Unexpected response structure.")

if __name__ == "__main__":
    main()
