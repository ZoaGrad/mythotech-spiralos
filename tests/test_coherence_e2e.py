import os
import pytest
import requests
import time
from datetime import datetime
from core.db import get_supabase
from core.scarindex import scar_index

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
# Mock URL for local testing if function not deployed, or use actual URL if available
# For this test, we might mock the ingestion or assume it's running locally via `supabase start`
# But since we can't easily run supabase locally here, we will simulate ingestion by writing to DB directly
# and then testing the ScarIndex logic which reads from DB.

def test_coherence_loop_e2e():
    """
    Verify the full Coherence Loop:
    1. Ingest Telemetry (simulate via DB insert for now, or mock function call)
    2. Compute ScarIndex (reads from DB)
    3. Verify Coherence Signal (writes to DB)
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        pytest.skip("Missing Supabase credentials")

    supabase = get_supabase()
    
    # 1. Simulate Telemetry Ingestion
    # In a real scenario, we'd POST to the Edge Function.
    # Here we insert directly to ensure the test is self-contained and doesn't depend on external function deployment yet.
    payload = {
        "event_type": "test_coherence_e2e",
        "source": "pytest",
        "payload": {"value": 123}
    }
    
    res = supabase.table("telemetry_events").insert(payload).execute()
    assert len(res.data) > 0
    event_id = res.data[0]['id']
    print(f"Inserted test event: {event_id}")
    
    # Wait a moment to ensure timestamp coverage
    time.sleep(1)
    
    # 2. Compute ScarIndex
    # This should pick up the event we just inserted (within default 5 min window)
    scar_value = scar_index.compute_scarindex_for_window(minutes=5)
    print(f"Computed ScarIndex: {scar_value}")
    
    # 3. Verify Coherence Signal
    # Check if a signal was written to coherence_signals
    res = supabase.table("coherence_signals") \
        .select("*") \
        .order("timestamp", desc=True) \
        .limit(1) \
        .execute()
        
    assert len(res.data) > 0
    signal = res.data[0]
    
    # Verify the signal corresponds to our calculation
    # Note: float comparison might need tolerance
    assert abs(signal['scarindex_value'] - scar_value) < 0.001
    assert signal['signal_data']['event_count'] >= 1 # Should include our event
    
    print("Coherence Loop Verified!")

if __name__ == "__main__":
    test_coherence_loop_e2e()
