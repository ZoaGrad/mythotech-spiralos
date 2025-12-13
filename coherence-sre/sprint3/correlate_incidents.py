#!/usr/bin/env python3
"""
Sprint 3: Temporal Correlator - Root Cause Hypothesis Generation
Links anomaly signals to incident events using temporal correlation and risk scoring.
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
LOOKBACK_HOURS = 6  # Look back 6 hours before incident
VARIANCE_THRESHOLD = 0.5  # 50% increase
TREND_WINDOW_HOURS = 6
SPIKE_MULTIPLIER = 3.0  # 3x rolling median


def fetch_events_from_supabase(client: Client, hours: int = 48) -> pd.DataFrame:
    """Fetch signal events from Supabase for the specified time range."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    print(f"Fetching events from {start_time.isoformat()} to {end_time.isoformat()}")
    
    try:
        # Fetch all events with pagination
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            response = client.table("signal_events") \
                .select("*") \
                .gte("ts", start_time.isoformat()) \
                .lte("ts", end_time.isoformat()) \
                .order("ts") \
                .range(offset, offset + page_size - 1) \
                .execute()
            
            if not response.data:
                break
            
            all_data.extend(response.data)
            
            if len(response.data) < page_size:
                break
            
            offset += page_size
        
        df = pd.DataFrame(all_data)
        
        if df.empty:
            print("Warning: No events found in the specified time range.", file=sys.stderr)
            return df
        
        # Convert timestamp to datetime with UTC timezone
        df['ts'] = pd.to_datetime(df['ts'], utc=True)
        df['value'] = pd.to_numeric(df['value'])
        
        print(f"Fetched {len(df)} events")
        print(f"Unique hosts: {df['host'].nunique()}")
        print()
        
        return df
    
    except Exception as e:
        print(f"Error fetching events: {e}", file=sys.stderr)
        return pd.DataFrame()


def detect_variance_escalation(df: pd.DataFrame, fingerprint: str, window_hours: int = 4) -> List[Dict[str, Any]]:
    """Detect variance escalation for a specific fingerprint."""
    events = []
    
    group = df[df['fingerprint'] == fingerprint].copy()
    if len(group) < 10:
        return events
    
    group = group.sort_values('ts').set_index('ts')
    
    # Resample into windows and calculate variance
    windowed = group['value'].resample(f"{window_hours}h").var().dropna()
    
    if len(windowed) < 2:
        return events
    
    first_variance = windowed.iloc[0]
    
    # Check each window for escalation
    for timestamp, variance in windowed.items():
        if first_variance < 0.01:
            if variance > 1.0:
                variance_multiplier = float('inf')
            else:
                continue
        else:
            variance_multiplier = variance / first_variance
        
        if variance_multiplier > (1 + VARIANCE_THRESHOLD):
            risk_score = min(1.0, (variance_multiplier - 1.0) / 2.0) if variance_multiplier != float('inf') else 1.0
            
            # Only include if risk score is significant
            if risk_score >= 0.5:
                host, metric = fingerprint.split(':', 1)
                events.append({
                    'detector': 'Variance Escalation',
                    'host': host,
                    'metric': metric,
                    'timestamp': timestamp,
                    'risk_score': risk_score,
                    'details': f"Variance escalated {variance_multiplier:.2f}x" if variance_multiplier != float('inf') else "Variance escalated ∞x"
                })
    
    return events


def detect_trend_breach(df: pd.DataFrame, fingerprint: str, window_hours: int = TREND_WINDOW_HOURS) -> List[Dict[str, Any]]:
    """Detect upward trends (resource exhaustion patterns)."""
    events = []
    
    group = df[df['fingerprint'] == fingerprint].copy()
    if len(group) < 20:
        return events
    
    group = group.sort_values('ts').set_index('ts')
    
    # Calculate rolling slope
    window_str = f"{window_hours}h"
    rolling_mean = group['value'].rolling(window_str).mean()
    
    # Calculate slope between consecutive windows
    slopes = rolling_mean.diff() / (window_hours * 3600)  # per second
    
    # Find periods of consistent positive slope
    positive_slope_threshold = 0.001  # Adjust based on metric scale
    
    for timestamp, slope in slopes.items():
        if pd.notna(slope) and slope > positive_slope_threshold:
            # Calculate risk score based on slope magnitude
            risk_score = min(0.8, abs(slope) * 1000)  # Scale to 0-0.8
            
            if risk_score >= 0.5:
                host, metric = fingerprint.split(':', 1)
                events.append({
                    'detector': 'Trend Breach',
                    'host': host,
                    'metric': metric,
                    'timestamp': timestamp,
                    'risk_score': risk_score,
                    'details': f"Rising at {slope * 3600:.2f} units/hr"
                })
    
    return events


def detect_spike(df: pd.DataFrame, fingerprint: str) -> List[Dict[str, Any]]:
    """Detect sudden spikes above rolling baseline."""
    events = []
    
    group = df[df['fingerprint'] == fingerprint].copy()
    if len(group) < 10:
        return events
    
    group = group.sort_values('ts').set_index('ts')
    
    # Calculate rolling median
    rolling_median = group['value'].rolling('2h', min_periods=5).median()
    
    # Find spikes (values > 3x rolling median)
    for timestamp, value in group['value'].items():
        median = rolling_median.loc[timestamp]
        
        if pd.notna(median) and median > 0 and value > (SPIKE_MULTIPLIER * median):
            risk_score = min(0.9, value / (SPIKE_MULTIPLIER * median) / 2)
            
            host, metric = fingerprint.split(':', 1)
            events.append({
                'detector': 'Spike',
                'host': host,
                'metric': metric,
                'timestamp': timestamp,
                'risk_score': risk_score,
                'details': f"Spike to {value:.2f} (baseline: {median:.2f})"
            })
    
    return events


def detect_all_risk_events(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Run all detectors in-memory and collect risk events."""
    print("Running in-memory detection algorithms...")
    
    all_events = []
    
    # Get unique fingerprints (excluding error metric)
    fingerprints = df[df['metric'] != 'error']['fingerprint'].unique()
    
    for fingerprint in fingerprints:
        # Run all detectors
        variance_events = detect_variance_escalation(df, fingerprint)
        trend_events = detect_trend_breach(df, fingerprint)
        spike_events = detect_spike(df, fingerprint)
        
        all_events.extend(variance_events)
        all_events.extend(trend_events)
        all_events.extend(spike_events)
    
    print(f"Detected {len(all_events)} risk events")
    return all_events


def find_incidents(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Identify incident events (severity='error')."""
    incidents = []
    
    error_events = df[df['severity'] == 'error'].copy()
    
    if error_events.empty:
        return incidents
    
    # Group by host and find incident windows
    for host in error_events['host'].unique():
        host_errors = error_events[error_events['host'] == host].sort_values('ts')
        
        # Group consecutive errors (within 10 minutes) into single incident
        current_incident = None
        
        for _, row in host_errors.iterrows():
            if current_incident is None:
                current_incident = {
                    'incident_id': row['id'],
                    'host': row['host'],
                    'timestamp': row['ts'],
                    'error_count': 1,
                    'first_error': row['ts'],
                    'last_error': row['ts']
                }
            else:
                time_diff = (row['ts'] - current_incident['last_error']).total_seconds() / 60
                
                if time_diff <= 10:
                    # Part of same incident
                    current_incident['error_count'] += 1
                    current_incident['last_error'] = row['ts']
                else:
                    # New incident
                    incidents.append(current_incident)
                    current_incident = {
                        'incident_id': row['id'],
                        'host': row['host'],
                        'timestamp': row['ts'],
                        'error_count': 1,
                        'first_error': row['ts'],
                        'last_error': row['ts']
                    }
        
        if current_incident:
            incidents.append(current_incident)
    
    print(f"Found {len(incidents)} incidents")
    return incidents


def correlate_incident(incident: Dict[str, Any], risk_events: List[Dict[str, Any]], lookback_hours: int = LOOKBACK_HOURS) -> List[Dict[str, Any]]:
    """Correlate risk events to an incident using temporal proximity and risk scoring."""
    hypotheses = []
    
    incident_time = incident['timestamp']
    incident_host = incident['host']
    lookback_start = incident_time - timedelta(hours=lookback_hours)
    
    # Filter risk events for same host within lookback window
    relevant_events = [
        e for e in risk_events
        if e['host'] == incident_host
        and lookback_start <= e['timestamp'] <= incident_time
    ]
    
    # Score each event by relevance
    for event in relevant_events:
        time_diff = (incident_time - event['timestamp']).total_seconds() / 3600  # hours
        
        # Relevance score: higher risk + closer in time = higher relevance
        relevance_score = event['risk_score'] / (time_diff + 0.1)
        
        hypotheses.append({
            'detector': event['detector'],
            'metric': event['metric'],
            'relevance': round(relevance_score, 2),
            'lead_time_hours': round(time_diff, 1),
            'risk_score': round(event['risk_score'], 2),
            'summary': event['details']
        })
    
    # Sort by relevance (highest first) and take top 3
    hypotheses = sorted(hypotheses, key=lambda x: x['relevance'], reverse=True)[:3]
    
    return hypotheses


def generate_incident_report(incidents: List[Dict[str, Any]], risk_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate root cause hypothesis report for all incidents."""
    reports = []
    
    for incident in incidents:
        hypotheses = correlate_incident(incident, risk_events)
        
        report = {
            'incident_id': incident['incident_id'],
            'host': incident['host'],
            'timestamp': incident['timestamp'].isoformat(),
            'error_count': incident['error_count'],
            'duration_minutes': round((incident['last_error'] - incident['first_error']).total_seconds() / 60, 1),
            'hypotheses': hypotheses
        }
        
        reports.append(report)
    
    return reports


def print_incident_report(reports: List[Dict[str, Any]]) -> None:
    """Print formatted incident correlation report."""
    if not reports:
        print("✅ No incidents detected. All systems stable.")
        return
    
    print("=" * 100)
    print("INCIDENT CORRELATION REPORT - ROOT CAUSE HYPOTHESES")
    print("=" * 100)
    print()
    
    for i, report in enumerate(reports, 1):
        print(f"INCIDENT #{i}")
        print("-" * 100)
        print(f"Host: {report['host']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Error Count: {report['error_count']}")
        print(f"Duration: {report['duration_minutes']} minutes")
        print()
        
        if report['hypotheses']:
            print("Top Probable Causes:")
            for j, hyp in enumerate(report['hypotheses'], 1):
                print(f"  {j}. [{hyp['detector']}] {hyp['metric']}")
                print(f"     Relevance: {hyp['relevance']} | Lead Time: {hyp['lead_time_hours']}h | Risk: {hyp['risk_score']}")
                print(f"     {hyp['summary']}")
                print()
        else:
            print("⚠️  No correlated risk events found in lookback window")
            print()
        
        print()
    
    print("=" * 100)


def main() -> int:
    """Main execution function."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not all([supabase_url, supabase_key]):
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Required: SUPABASE_URL, SUPABASE_KEY", file=sys.stderr)
        return 1
    
    print("=" * 100)
    print("SPRINT 3: TEMPORAL CORRELATOR - ROOT CAUSE HYPOTHESIS GENERATION")
    print("=" * 100)
    print()
    
    # Initialize Supabase client
    client = create_client(supabase_url, supabase_key)
    
    # Step A: Fetch data
    df = fetch_events_from_supabase(client, hours=48)
    
    if df.empty:
        print("No data to analyze.", file=sys.stderr)
        return 1
    
    # Step B: Detect risk events (in-memory)
    risk_events = detect_all_risk_events(df)
    print()
    
    # Step C: Find incidents
    incidents = find_incidents(df)
    print()
    
    # Step D: Correlate incidents to risk events
    print("Correlating incidents to risk events...")
    reports = generate_incident_report(incidents, risk_events)
    print()
    
    # Step E: Output
    print_incident_report(reports)
    
    # Also output JSON for programmatic use
    json_output = json.dumps(reports, indent=2)
    
    # Save to file
    output_file = "incident_correlation_report.json"
    with open(output_file, 'w') as f:
        f.write(json_output)
    
    print(f"JSON report saved to: {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
