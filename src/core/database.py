import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from the sovereign root
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("CRITICAL: Sovereign Credentials (SUPABASE_URL/KEY) missing from .env")

# Initialize the Sovereign Client
supabase: Client = create_client(url, key)

def get_vault_client() -> Client:
    """Returns the active connection to the Truth Vault."""
    return supabase

def get_economic_metrics() -> dict:
    """
    Retrieves the aggregated economic snapshot from the Vault (RPC).
    Returns:
        dict: { 'total_supply': float, 'lifetime_avg': float, 'current_yield': float }
    """
    try:
        response = supabase.rpc('get_economic_snapshot', {}).execute()
        if response.data:
            return response.data
        return {"total_supply": 0.0, "lifetime_avg": 0.0, "current_yield": 0.0}
    except Exception as e:
        print(f"WARNING: Failed to fetch economic metrics: {e}")
        return {"total_supply": 0.0, "lifetime_avg": 0.0, "current_yield": 0.0}

def create_wallet(user_id: str) -> bool:
    """
    Creates a new wallet for the given user_id.
    Returns True if created or already exists, False on error.
    """
    try:
        # Insert with ON CONFLICT DO NOTHING behavior handled by SQL or simple check
        # Using upsert or insert with ignore. 
        # Since we want to be safe, we can just try insert and catch error or use upsert.
        # Supabase-py upsert:
        data = {"user_id": user_id, "balance": 0.0}
        supabase.table("wallets").upsert(data, on_conflict="user_id", ignore_duplicates=True).execute()
        return True
    except Exception as e:
        print(f"ERROR: Failed to create wallet for {user_id}: {e}")
        return False

def get_wallet_balance(user_id: str) -> float:
    """
    Retrieves the balance for a user.
    Returns 0.0000 if user not found (Auto-Genesis logic handled by caller or here).
    """
    try:
        response = supabase.table("wallets").select("balance").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return float(response.data[0]['balance'])
        return 0.0
    except Exception as e:
        print(f"WARNING: Failed to fetch balance for {user_id}: {e}")
        return 0.0

def execute_transfer(sender: str, receiver: str, amount: float) -> bool:
    """
    Executes an atomic transfer via RPC.
    Returns True if successful, False if insufficient funds or error.
    """
    try:
        payload = {"sender": sender, "receiver": receiver, "amt": amount}
        response = supabase.rpc("transfer_scar", payload).execute()
        # RPC returns boolean directly in data
        if response.data is True:
            return True
        return False
    except Exception as e:
        print(f"CRITICAL: Transfer failed (RPC Error): {e}")
        return False
