import os
from supabase import create_client, Client

_supabase: Client | None = None

def get_supabase() -> Client:
    """
    Returns a singleton Supabase client instance.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.
    """
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.")
            
        _supabase = create_client(url, key)
    return _supabase
