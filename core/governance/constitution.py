from typing import List, Dict, Any
import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def load_constitution() -> List[Dict[str, Any]]:
    """
    Fetches all active constitutional articles, ordered by article number.
    """
    supabase = get_supabase()
    response = supabase.table("core_constitution") \
        .select("*") \
        .eq("superseded", False) \
        .order("article_number", desc=False) \
        .execute()
    return response.data
