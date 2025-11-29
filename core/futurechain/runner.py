# core/futurechain/runner.py
import time
from core.db import db
from core.futurechain.extend import extend_chain_from_lattice

def process_future_chain(client=None):
    """
    Scans for recent lattice nodes that do NOT have a corresponding future_chain entry,
    and extends them.
    """
    if not client:
        client = db.client._ensure_client()
        
    # 1. Find candidates
    # We want lattice nodes created recently that are NOT in future_chain
    # This requires a join or a "not in" query.
    # Supabase/PostgREST doesn't support complex "NOT IN" subqueries easily via JS client.
    # So we'll use a custom RPC or a raw SQL query if possible, OR just fetch recent lattice nodes 
    # and check existence (less efficient but works for now).
    
    # Let's fetch recent lattice nodes (last 1 hour)
    # And we'll just try to extend them. The RPC logic could be made idempotent or we check here.
    # Actually, let's just fetch recent lattice nodes and try to extend. 
    # Ideally we'd have an index or a flag "projected" on integration_lattice, but we can't modify that table easily now.
    
    # Better approach: Fetch recent lattice nodes, and for each, check if we already projected it.
    # To optimize, we can fetch all future_chain entries for the last hour and diff them in memory.
    
    try:
        # Get recent lattice nodes
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        
        lattice_res = client.table("integration_lattice").select("id").gte("created_at", cutoff).execute()
        lattice_ids = {row['id'] for row in (lattice_res.data or [])}
        
        if not lattice_ids:
            return 0
            
        # Get recent chain entries
        chain_res = client.table("future_chain").select("lattice_id").gte("created_at", cutoff).execute()
        existing_ids = {row['lattice_id'] for row in (chain_res.data or [])}
        
        # Diff
        to_process = lattice_ids - existing_ids
        
        count = 0
        for lid in to_process:
            new_id = extend_chain_from_lattice(lid)
            if new_id:
                count += 1
                
        if count > 0:
            print(f"[FUTURECHAIN] Extended {count} new timeline nodes.")
            
        return count
        
    except Exception as e:
        print(f"[FUTURECHAIN_RUNNER_ERROR] {e}")
        return 0

def run_future_chain_loop(interval=15):
    print("♾️ [FUTURECHAIN] Runner started.")
    client = db.client._ensure_client()
    while True:
        process_future_chain(client)
        time.sleep(interval)

if __name__ == "__main__":
    run_future_chain_loop()
