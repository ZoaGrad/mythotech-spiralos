import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

def verify_breath():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("ERROR: Missing Supabase credentials")
        return

    supabase = create_client(url, key)
    
    print(">>> Querying Ledger for First Breath...")
    
    # Fetch the latest entry
    response = supabase.table("attestations")\
        .select("*")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
    
    if response.data and len(response.data) > 0:
        latest = response.data[0]
        print(f"LATEST ATTESTATION FOUND:")
        print(f"   - ID: {latest.get('id')}")
        print(f"   - Source: {latest.get('source')}")
        print(f"   - Description: {latest.get('description')}")
        print(f"   - WI Score: {latest.get('final_wi_score')}")
        print(f"   - Created At: {latest.get('created_at')}")
        
        if "Stamp the Sovereign Seal" in latest.get("description", ""):
            print("\nCONFIRMED: The First Breath has been recorded.")
        else:
            print("\nWARNING: Latest entry does not match the First Breath commit.")
    else:
        print("ERROR: Ledger is empty or read failed.")

if __name__ == "__main__":
    verify_breath()
