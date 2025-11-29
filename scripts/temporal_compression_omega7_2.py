# scripts/temporal_compression_omega7_2.py
import sys
import os
import time
import json
import random
import statistics
import concurrent.futures
from datetime import datetime, timezone

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.audit_emitter import emit_audit_event
from core.causality_emitter import link_events
from core.db import db

# Configuration
TOTAL_EVENTS = 1000
WORKERS = 10
TARGET_DURATION_SEC = 10.0

def worker_task(iteration):
    """
    Executes a single fusion cascade:
    Emit Source -> Emit Target -> Link (Fusion -> Paradox -> Lattice -> Guardian)
    """
    start_ts = time.time()
    result = {
        "iteration": iteration,
        "success": False,
        "duration_ms": 0,
        "error": None
    }
    
    try:
        # We use a fresh client or rely on thread-safety of the singleton?
        # supabase-py is generally thread-safe for HTTP requests.
        
        # 1. Emit Source
        source_id = emit_audit_event(
            event_type="compression_test_source",
            component="TemporalCompressor",
            payload={"iteration": iteration, "role": "source"}
        )
        
        # 2. Emit Target
        target_id = emit_audit_event(
            event_type="compression_test_target",
            component="TemporalCompressor",
            payload={"iteration": iteration, "role": "target"}
        )
        
        if source_id and target_id:
            # 3. Link (The Heavy Lift)
            link_id = link_events(
                source_event_id=source_id,
                target_event_id=target_id,
                cause_type="TEMPORAL_COMPRESSION",
                weight=random.uniform(0.7, 0.99),
                severity="RED",
                notes={"compression_iteration": iteration}
            )
            
            if link_id:
                result["success"] = True
            else:
                result["error"] = "Link creation failed (returned None)"
        else:
            result["error"] = "Event emission failed"
            
    except Exception as e:
        result["error"] = str(e)
        
    end_ts = time.time()
    result["duration_ms"] = (end_ts - start_ts) * 1000.0
    return result

def run_compression_test():
    print(f"🚀 [Ω.7.2] Starting Temporal Compression Test")
    print(f"   Target: {TOTAL_EVENTS} events in <{TARGET_DURATION_SEC}s")
    print(f"   Workers: {WORKERS}")
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(worker_task, i): i for i in range(TOTAL_EVENTS)}
        
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results.append(res)
            completed += 1
            if completed % 100 == 0:
                elapsed = time.time() - start_time
                print(f"   ... {completed}/{TOTAL_EVENTS} ({elapsed:.2f}s)")

    total_duration = time.time() - start_time
    
    # Analysis
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]
    durations = [r["duration_ms"] for r in successes]
    
    metrics = {
        "total_events": TOTAL_EVENTS,
        "successful_cascades": len(successes),
        "failed_cascades": len(failures),
        "total_duration_sec": total_duration,
        "throughput_ops_sec": len(successes) / total_duration if total_duration > 0 else 0,
        "latency_ms": {
            "min": min(durations) if durations else 0,
            "max": max(durations) if durations else 0,
            "avg": statistics.mean(durations) if durations else 0,
            "p50": statistics.median(durations) if durations else 0,
            "p95": statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else 0,
            "p99": statistics.quantiles(durations, n=100)[98] if len(durations) >= 100 else 0
        }
    }
    
    print("\n📊 [COMPRESSION REPORT]")
    print(json.dumps(metrics, indent=2))
    
    if failures:
        print(f"\n⚠️ {len(failures)} Failures Detected. Sample errors:")
        for f in failures[:5]:
            print(f" - Iter {f['iteration']}: {f['error']}")
            
    # Check Target
    if total_duration < TARGET_DURATION_SEC:
        print(f"\n✅ SUCCESS: Compressed {len(successes)} events in {total_duration:.2f}s (<{TARGET_DURATION_SEC}s)")
    else:
        print(f"\n⚠️ WARNING: Time target missed. {total_duration:.2f}s > {TARGET_DURATION_SEC}s")

if __name__ == "__main__":
    run_compression_test()
