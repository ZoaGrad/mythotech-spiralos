"""
SPIRAL_OS // SCRIPTS // MINT_GENESIS
------------------------------------
Identity: The Coronation Mint
Mandate: Insert the Genesis Record into ScarIndex.
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def mint_genesis():
    load_dotenv()
    
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("❌ CRITICAL: Supabase credentials missing.")
        sys.exit(1)

    print(">>> [MINT] Connecting to Supabase...")
    supabase: Client = create_client(url, key)

    print(">>> [MINT] Forging Genesis Record...")
    data = {
        "value": 1.0,
        "narrative_status": "EVENT: The Great Wipe Complete. Sovereignty Restored. Genesis Coin Minted.",
        # created_at is handled by default or we can let DB handle it, but user SQL had NOW().
        # Supabase usually handles created_at automatically if not provided.
    }

    try:
        response = supabase.table("scar_index").insert(data).execute()
        print(">>> [SUCCESS] Genesis Coin Minted.")
        print(f">>> [RECORD] {response.data}")
    except Exception as e:
        print(f"❌ [ERROR] Minting Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    mint_genesis()
