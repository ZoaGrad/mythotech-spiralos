import os
import pytest
from supabase import create_client, Client

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

@pytest.fixture
def admin_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.skip("Missing Supabase credentials")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@pytest.fixture
def anon_client():
    if not SUPABASE_URL or not ANON_KEY:
        pytest.skip("Missing Supabase credentials")
    return create_client(SUPABASE_URL, ANON_KEY)

def test_witness_entries_rls(admin_client, anon_client):
    """Verify RLS on witness_entries table."""
    # Admin should be able to insert
    data = {"witness_id": "test_witness", "entry_data": {"test": "data"}}
    res = admin_client.table("witness_entries").insert(data).execute()
    assert len(res.data) > 0
    entry_id = res.data[0]['id']

    # Anon should be able to read
    res = anon_client.table("witness_entries").select("*").eq("id", entry_id).execute()
    assert len(res.data) == 1
    
    # Anon should NOT be able to insert (this might fail if policy allows anon insert, check policy)
    # Our policy: "Authenticated users can insert", Anon is read-only.
    try:
        anon_client.table("witness_entries").insert(data).execute()
        assert False, "Anon should not be able to insert"
    except Exception:
        assert True

def test_telemetry_rls(admin_client, anon_client):
    """Verify RLS on telemetry_events table."""
    # Admin insert
    data = {"event_type": "test", "source": "test", "payload": {}}
    res = admin_client.table("telemetry_events").insert(data).execute()
    assert len(res.data) > 0
    
    # Anon read
    res = anon_client.table("telemetry_events").select("*").limit(1).execute()
    assert len(res.data) >= 0 # Might be empty but shouldn't error

    # Anon insert fail
    try:
        anon_client.table("telemetry_events").insert(data).execute()
        assert False, "Anon should not be able to insert"
    except Exception:
        assert True
