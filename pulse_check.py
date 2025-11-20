import os
from dotenv import load_dotenv
from supabase import create_client
import pathlib


# Debug: Print current working directory and .env file existence
print("-" * 30)
print(">>> SYSTEM PULSE CHECK")
print("-" * 30)
print(f"Current working directory: {os.getcwd()}")
env_path = pathlib.Path(".env")

print(f".env file exists: {env_path.resolve()} -> {env_path.exists()}")
if env_path.exists():
    with open(env_path, 'rb') as f:
        raw = f.read()
    print(f".env raw bytes: {raw}")
    try:
        text = raw.decode('utf-8')
        print(f".env utf-8 text:\n{text}")
    except Exception as e:
        print(f"Could not decode .env as utf-8: {e}")

# 1. Load the Secrets
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# 2. Verify Keys Exist
if not url or not key:
    print("❌ CRITICAL: .env keys are MISSING.")
    print("   Action: Create a .env file with SUPABASE_URL and SUPABASE_KEY.")
    print(f"   SUPABASE_URL: {url}")
    print(f"   SUPABASE_KEY: {key}")
    exit()

print("✅ Keys Detected.")
print(f"   Target: {url}")

# 3. Attempt Connection
try:
    print(">>> Attempting Handshake with Supabase...")
    supabase = create_client(url, key)
    
    # Simple fetch to prove connection (doesn't read data, just checks auth)
    # We assume a table exists, or we just check the object creation
    print("✅ Client Created Successfully.")
    
    # Optional: Try to read the 'scar_index' table if it exists
    try:
        response = supabase.table("scar_index").select("*").limit(1).execute()
        print("✅ DATABASE READ: SUCCESS.")
        print("   The Golem is AWAKE.")
    except Exception as db_e:
        print(f"⚠️  Auth worked, but Table Read failed: {db_e}")
        print("   (This is fine. It means we are connected but the table is missing/empty.)")

except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")

print("-" * 30)
