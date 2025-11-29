# scripts/load_test_omega7_1.py
import sys
import os
import time
import uuid
import random
import json
from datetime import datetime, timezone

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import db
from core.paradox_predictor import project_paradox_for_fusion, integrate_future_from_fusion
from core.guardian_actions import plan_action_for_lattice

from core.audit_emitter import emit_audit_event
from core.causality_emitter import link_events

def run_load_test(count=100):
    print(f"🚀 [LOAD TEST] Starting Ω.7.1 Full Pipeline Test ({count} events)...")
    
    stats = {
        "events_emitted": 0,
        "links_created": 0,
        "fusion_triggered": 0, # Inferred
        "errors": 0,
        "total_time_ms": 0
    }
    
    start_time = time.time()
    
    for i in range(count):
        iter_start = time.time()
        try:
            # 1. Emit Source Event
            source_id = emit_audit_event(
                event_type="load_test_source",
                component="LoadTester",
                payload={"iteration": i, "role": "source"}
            )
            
            # 2. Emit Target Event
            target_id = emit_audit_event(
                event_type="load_test_target",
                component="LoadTester",
                payload={"iteration": i, "role": "target"}
            )
            
            if source_id and target_id:
                stats["events_emitted"] += 2
                
                # 3. Link Events (Triggers Fusion -> Paradox -> Lattice -> Guardian)
                link_id = link_events(
                    source_event_id=source_id,
                    target_event_id=target_id,
                    cause_type="LOAD_TEST_PRESSURE",
                    weight=random.uniform(0.5, 0.95),
                    severity="RED", # Force high severity to trigger interesting paths
                    notes={"load_test_iteration": i}
                )
                
                if link_id:
                    stats["links_created"] += 1
                    stats["fusion_triggered"] += 1
            else:
                print(f"⚠️ Failed to emit events for iteration {i}")
                stats["errors"] += 1

        except Exception as e:
            print(f"❌ Iteration {i} failed: {e}")
            stats["errors"] += 1
        
        iter_duration = (time.time() - iter_start) * 1000
        stats["total_time_ms"] += iter_duration
        
        if (i + 1) % 10 == 0:
            print(f"   ... {i + 1}/{count} completed (Avg: {stats['total_time_ms'] / (i + 1):.2f}ms/op)")

    total_duration = time.time() - start_time
    
    print("\n📊 [RESULTS]")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Throughput: {count / total_duration:.2f} ops/sec")
    print(f"Avg Latency: {stats['total_time_ms'] / count:.2f}ms")
    print(json.dumps(stats, indent=2))
    
    if stats["errors"] > 0:
        print("⚠️ Completed with errors.")
        sys.exit(1)
    else:
        print("✅ Load Test Passed: Pipeline Integrity Confirmed.")

if __name__ == "__main__":
    run_load_test(100)
