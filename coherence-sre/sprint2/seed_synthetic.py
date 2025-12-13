#!/usr/bin/env python3
"""
Flight Simulator for Coherence SRE Platform
Generates 48 hours of synthetic metric data with contrasting host profiles.
"""

import os
import sys
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
BATCH_SIZE = 500  # Insert rows in batches to avoid API timeouts
TIME_RANGE_HOURS = 48
SAMPLE_INTERVAL_MINUTES = 5  # One data point every 5 minutes
INCIDENT_TIME_OFFSET_HOURS = 12  # Incident occurs 12 hours ago


def generate_healthy_host_data(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Generate data for a healthy host with low variance and no spikes.
    
    Args:
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of event dictionaries
    """
    events = []
    current_time = start_time
    
    while current_time <= end_time:
        # CPU: Low variance, 10-25%
        cpu_value = random.uniform(10.0, 25.0)
        events.append({
            "ts": current_time.isoformat(),
            "host": "host-healthy",
            "service": "system",
            "fingerprint": "host-healthy:cpu",
            "severity": "info",
            "metric": "cpu",
            "value": round(cpu_value, 2),
            "synthetic": True
        })
        
        # Memory: Stable, 30-45%
        memory_value = random.uniform(30.0, 45.0)
        events.append({
            "ts": current_time.isoformat(),
            "host": "host-healthy",
            "service": "system",
            "fingerprint": "host-healthy:memory",
            "severity": "info",
            "metric": "memory",
            "value": round(memory_value, 2),
            "synthetic": True
        })
        
        current_time += timedelta(minutes=SAMPLE_INTERVAL_MINUTES)
    
    return events


def generate_stressed_host_data(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """
    Generate data for a stressed host with spikes, memory leak, and incident burst.
    
    Args:
        start_time: Start of time range
        end_time: End of time range
        
    Returns:
        List of event dictionaries
    """
    events = []
    current_time = start_time
    
    # Calculate incident time (12 hours ago from end_time)
    incident_start = end_time - timedelta(hours=INCIDENT_TIME_OFFSET_HOURS)
    incident_end = incident_start + timedelta(hours=1)
    
    # Calculate total duration for memory leak simulation
    total_duration = (end_time - start_time).total_seconds()
    
    while current_time <= end_time:
        elapsed = (current_time - start_time).total_seconds()
        
        # CPU: Baseline 20-35%, with massive spikes every 6 hours
        hours_since_start = elapsed / 3600
        is_spike_time = (hours_since_start % 6) < 0.5  # Spike for 30 minutes every 6 hours
        
        if is_spike_time:
            cpu_value = random.uniform(85.0, 95.0)
            severity = "error"
        else:
            cpu_value = random.uniform(20.0, 35.0)
            severity = "info"
        
        events.append({
            "ts": current_time.isoformat(),
            "host": "host-stressed",
            "service": "system",
            "fingerprint": "host-stressed:cpu",
            "severity": severity,
            "metric": "cpu",
            "value": round(cpu_value, 2),
            "synthetic": True
        })
        
        # Memory: Linear growth from 40% to 95% (simulating leak)
        memory_baseline = 40.0
        memory_growth = (elapsed / total_duration) * 55.0  # Grow 55% over 48 hours
        memory_value = memory_baseline + memory_growth + random.uniform(-2.0, 2.0)
        memory_value = min(memory_value, 95.0)  # Cap at 95%
        
        memory_severity = "error" if memory_value > 80 else ("warn" if memory_value > 60 else "info")
        
        events.append({
            "ts": current_time.isoformat(),
            "host": "host-stressed",
            "service": "system",
            "fingerprint": "host-stressed:memory",
            "severity": memory_severity,
            "metric": "memory",
            "value": round(memory_value, 2),
            "synthetic": True
        })
        
        # Incident burst: 12 error events during the incident window
        if incident_start <= current_time <= incident_end:
            # Generate error event
            events.append({
                "ts": current_time.isoformat(),
                "host": "host-stressed",
                "service": "application",
                "fingerprint": "host-stressed:error",
                "severity": "error",
                "metric": "error",
                "value": 1,
                "synthetic": True
            })
        
        current_time += timedelta(minutes=SAMPLE_INTERVAL_MINUTES)
    
    return events


def insert_events_in_batches(client: Client, events: List[Dict[str, Any]], batch_size: int = BATCH_SIZE) -> int:
    """
    Insert events into Supabase in batches to avoid API timeouts.
    
    Args:
        client: Supabase client
        events: List of event dictionaries
        batch_size: Number of rows per batch
        
    Returns:
        Total number of events inserted
    """
    total_inserted = 0
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        
        try:
            response = client.table("signal_events").insert(batch).execute()
            total_inserted += len(batch)
            print(f"  Inserted batch {i // batch_size + 1}: {len(batch)} events (total: {total_inserted})")
        except Exception as e:
            print(f"  Error inserting batch {i // batch_size + 1}: {e}", file=sys.stderr)
            # Continue with next batch instead of failing completely
    
    return total_inserted


def main() -> int:
    """
    Main execution function for synthetic data generation.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load configuration from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not all([supabase_url, supabase_key]):
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Required: SUPABASE_URL, SUPABASE_KEY", file=sys.stderr)
        return 1
    
    # Calculate time range (past 48 hours to now)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=TIME_RANGE_HOURS)
    
    print(f"Generating synthetic data from {start_time.isoformat()} to {end_time.isoformat()}")
    print(f"Sample interval: {SAMPLE_INTERVAL_MINUTES} minutes")
    print(f"Batch size: {BATCH_SIZE} rows")
    print()
    
    # Generate data for both hosts
    print("Generating data for host-healthy (low variance, stable)...")
    healthy_events = generate_healthy_host_data(start_time, end_time)
    print(f"  Generated {len(healthy_events)} events")
    
    print("Generating data for host-stressed (spikes, memory leak, incident burst)...")
    stressed_events = generate_stressed_host_data(start_time, end_time)
    print(f"  Generated {len(stressed_events)} events")
    
    # Combine all events
    all_events = healthy_events + stressed_events
    print(f"\nTotal events to insert: {len(all_events)}")
    print()
    
    # Initialize Supabase client
    client = create_client(supabase_url, supabase_key)
    
    # Insert events in batches
    print("Inserting events into Supabase...")
    total_inserted = insert_events_in_batches(client, all_events)
    
    print()
    print(f"✅ Successfully inserted {total_inserted} events")
    print(f"   - host-healthy: {len(healthy_events)} events")
    print(f"   - host-stressed: {len(stressed_events)} events")
    print()
    print("Flight Simulator data seeding complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
