# scripts/load_test_omega8.py
import sys
import os
import time
import json
import random
import concurrent.futures
from datetime import datetime, timezone

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.audit_emitter import emit_audit_event
from core.causality_emitter import link_events
from core.futurechain.runner import process_future_chain
from core.db import db

# Configuration
TOTAL_EVENTS = 3000
WORKERS = 15
TARGET_DURATION_SEC = 30.0

def worker_task(iteration):
    try:
        source_id = emit_audit_event(
            event_type="futurechain_stress_source",
            component="Omega8Tester",
            payload={"iteration": iteration}
        )
        target_id = emit_audit_event(
            event_type="futurechain_stress_target",
            component="Omega8Tester",
            payload={"iteration": iteration}
        )
        
        if source_id and target_id:
            link_events(
                source_event_id=source_id,
                target_event_id=target_id,
                cause_type="FUTURE_CHAIN_STRESS",
                weight=random.uniform(0.1, 0.9),
                severity="RED" if random.random() > 0.8 else "LOW",
                notes={"omega8_iteration": iteration}
            )
            return True
    except:
        return False
    return False

def run_load_test():
    print(f"🚀 [Ω.8] Starting FutureChain Stress Test")
    print(f"   Target: {TOTAL_EVENTS} events")
    
    start_time = time.time()
    
    # 1. Generate Load
    print("   Generating load...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(worker_task, i) for i in range(TOTAL_EVENTS)]
        concurrent.futures.wait(futures)
        
    load_duration = time.time() - start_time
    print(f"   Load generation complete in {load_duration:.2f}s")
    
    # 2. Run Chain Extension (Simulating Runner)
    print("   Processing FutureChain extensions...")
    chain_start = time.time()
    
    # We loop until we process a good chunk or run out of candidates
    total_extended = 0
    client = db.client._ensure_client()
    
    # Give the DB a moment to settle/index
    time.sleep(2)
    
    # Run the processor in a loop until it returns 0 for a few times
    empty_runs = 0
    while empty_runs < 3:
        count = process_future_chain(client)
        if count > 0:
            total_extended += count
            empty_runs = 0
            print(f"   ... extended {count} nodes")
        else:
            empty_runs += 1
            time.sleep(1)
            
    chain_duration = time.time() - chain_start
    
    print("\n📊 [Ω.8 REPORT]")
    print(f"Events Generated: {TOTAL_EVENTS}")
    print(f"Chain Extensions: {total_extended}")
    print(f"Load Duration: {load_duration:.2f}s")
    print(f"Chain Processing Duration: {chain_duration:.2f}s")
    
    if total_extended > 0:
        print("✅ FutureChain is active and extending.")
    else:
        print("⚠️ No chain extensions occurred. Check pipeline.")

if __name__ == "__main__":
    run_load_test()
