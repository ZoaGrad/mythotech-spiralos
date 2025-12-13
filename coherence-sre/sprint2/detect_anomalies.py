#!/usr/bin/env python3
"""
Sprint 2: Multi-Modal Anomaly Detection Suite
Implements three complementary detectors: variance escalation, spike detection, and trend analysis.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
WINDOW_SIZE_HOURS = 4
VARIANCE_THRESHOLD = 0.5  # 50% increase
SPIKE_THRESHOLD = 2.5  # 2.5 standard deviations above mean
TREND_THRESHOLD = 0.3  # 30% increase over time period


def fetch_events_from_supabase(client: Client, hours: int = 48) -> pd.DataFrame:
    """Fetch signal events from Supabase for the specified time range."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    print(f"Fetching events from {start_time.isoformat()} to {end_time.isoformat()}")
    
    try:
        # Fetch all events with pagination (Supabase default limit is 1000)
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
        
        df['ts'] = pd.to_datetime(df['ts'])
        df['value'] = pd.to_numeric(df['value'])
        
        print(f"Fetched {len(df)} events")
        print(f"Unique hosts: {df['host'].nunique()}")
        print(f"Unique fingerprints: {df['fingerprint'].nunique()}")
        print()
        
        return df
    
    except Exception as e:
        print(f"Error fetching events: {e}", file=sys.stderr)
        return pd.DataFrame()


def detect_variance_escalation(df: pd.DataFrame, window_hours: int = WINDOW_SIZE_HOURS) -> List[Dict[str, Any]]:
    """Detect increasing chaos/volatility in metrics."""
    alerts = []
    
    for fingerprint, group in df.groupby('fingerprint'):
        group = group.sort_values('ts').set_index('ts')
        
        # Resample into windows and calculate variance
        windowed = group['value'].resample(f"{window_hours}h").var().dropna()
        
        if len(windowed) < 2:
            continue
        
        first_variance = windowed.iloc[0]
        last_variance = windowed.iloc[-1]
        
        if first_variance < 0.01:
            if last_variance > 1.0:
                variance_multiplier = float('inf')
            else:
                continue
        else:
            variance_multiplier = last_variance / first_variance
        
        if variance_multiplier > (1 + VARIANCE_THRESHOLD):
            host, metric = fingerprint.split(':', 1)
            risk_score = min(1.0, (variance_multiplier - 1.0) / 2.0) if variance_multiplier != float('inf') else 1.0
            
            alerts.append({
                'detector': 'variance_escalation',
                'host': host,
                'metric': metric,
                'fingerprint': fingerprint,
                'multiplier': variance_multiplier,
                'risk_score': risk_score,
                'details': f"Variance escalated {variance_multiplier:.2f}x" if variance_multiplier != float('inf') else "Variance escalated ∞x"
            })
    
    return alerts


def detect_spikes(df: pd.DataFrame, threshold_std: float = SPIKE_THRESHOLD) -> List[Dict[str, Any]]:
    """Detect sudden spikes above normal baseline."""
    alerts = []
    
    for fingerprint, group in df.groupby('fingerprint'):
        group = group.sort_values('ts')
        values = group['value'].values
        
        # Calculate baseline statistics (mean and std)
        mean = np.mean(values)
        std = np.std(values)
        
        if std < 0.01:
            # No variation, skip
            continue
        
        # Find spikes (values > mean + threshold * std)
        spike_threshold = mean + (threshold_std * std)
        spikes = values > spike_threshold
        spike_count = np.sum(spikes)
        
        if spike_count > 0:
            spike_percentage = (spike_count / len(values)) * 100
            max_spike_value = np.max(values[spikes])
            
            # Calculate risk score based on spike frequency and magnitude
            frequency_score = min(1.0, spike_percentage / 10.0)  # 10% spikes = 1.0
            magnitude_score = min(1.0, (max_spike_value - mean) / (3 * std))
            risk_score = (frequency_score + magnitude_score) / 2
            
            host, metric = fingerprint.split(':', 1)
            
            alerts.append({
                'detector': 'spike_detection',
                'host': host,
                'metric': metric,
                'fingerprint': fingerprint,
                'spike_count': spike_count,
                'spike_percentage': spike_percentage,
                'max_spike': max_spike_value,
                'baseline_mean': mean,
                'risk_score': risk_score,
                'details': f"{spike_count} spikes ({spike_percentage:.1f}%), max: {max_spike_value:.2f} (baseline: {mean:.2f})"
            })
    
    return alerts


def detect_trends(df: pd.DataFrame, threshold: float = TREND_THRESHOLD) -> List[Dict[str, Any]]:
    """Detect upward/downward trends (e.g., memory leaks, resource exhaustion)."""
    alerts = []
    
    for fingerprint, group in df.groupby('fingerprint'):
        group = group.sort_values('ts')
        values = group['value'].values
        
        if len(values) < 10:
            continue
        
        # Calculate linear regression trend
        x = np.arange(len(values))
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        
        # Calculate percentage change from start to end
        first_value = values[0]
        last_value = values[-1]
        
        if first_value < 0.01:
            continue
        
        percentage_change = (last_value - first_value) / first_value
        
        # Check for significant upward trend
        if percentage_change > threshold:
            host, metric = fingerprint.split(':', 1)
            
            # Risk score based on magnitude of change
            risk_score = min(1.0, percentage_change / 1.0)  # 100% change = 1.0
            
            alerts.append({
                'detector': 'trend_detection',
                'host': host,
                'metric': metric,
                'fingerprint': fingerprint,
                'percentage_change': percentage_change * 100,
                'slope': slope,
                'start_value': first_value,
                'end_value': last_value,
                'risk_score': risk_score,
                'details': f"Upward trend: {percentage_change*100:.1f}% increase ({first_value:.2f} → {last_value:.2f})"
            })
    
    return alerts


def print_detection_report(all_alerts: List[Dict[str, Any]]) -> None:
    """Print comprehensive detection report."""
    if not all_alerts:
        print("✅ No anomalies detected. All systems stable.")
        return
    
    # Sort by risk score
    all_alerts = sorted(all_alerts, key=lambda x: x['risk_score'], reverse=True)
    
    print("=" * 100)
    print("MULTI-MODAL ANOMALY DETECTION REPORT")
    print("=" * 100)
    print()
    
    # Group by detector type
    by_detector = {}
    for alert in all_alerts:
        detector = alert['detector']
        if detector not in by_detector:
            by_detector[detector] = []
        by_detector[detector].append(alert)
    
    # Print each detector's findings
    for detector_name, alerts in by_detector.items():
        print(f"🔍 {detector_name.upper().replace('_', ' ')}")
        print("-" * 100)
        
        for alert in alerts:
            host = alert['host']
            metric = alert['metric']
            risk_score = alert['risk_score']
            details = alert['details']
            
            # Risk level emoji
            if risk_score >= 0.8:
                risk_emoji = "🔴"
            elif risk_score >= 0.5:
                risk_emoji = "🟡"
            else:
                risk_emoji = "🟢"
            
            print(f"{risk_emoji} [RISK ALERT] {host}:{metric} → {details} (Risk: {risk_score:.2f})")
        
        print()
    
    print("=" * 100)
    print(f"Total alerts: {len(all_alerts)} across {len(by_detector)} detector types")
    print("=" * 100)


def print_summary_statistics(df: pd.DataFrame, all_alerts: List[Dict[str, Any]]) -> None:
    """Print summary statistics."""
    print()
    print("SUMMARY STATISTICS")
    print("-" * 100)
    print()
    
    # Per-host summary
    for host in df['host'].unique():
        host_data = df[df['host'] == host]
        host_alerts = [a for a in all_alerts if a['host'] == host]
        
        print(f"Host: {host}")
        print(f"  Total events: {len(host_data)}")
        print(f"  Metrics tracked: {host_data['metric'].nunique()}")
        print(f"  Alerts triggered: {len(host_alerts)}")
        
        if host_alerts:
            avg_risk = np.mean([a['risk_score'] for a in host_alerts])
            max_risk = np.max([a['risk_score'] for a in host_alerts])
            print(f"  Average risk score: {avg_risk:.2f}")
            print(f"  Maximum risk score: {max_risk:.2f}")
        
        print()


def main() -> int:
    """Main execution function."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not all([supabase_url, supabase_key]):
        print("Error: Missing required environment variables.", file=sys.stderr)
        print("Required: SUPABASE_URL, SUPABASE_KEY", file=sys.stderr)
        return 1
    
    print("=" * 100)
    print("SPRINT 2: MULTI-MODAL ANOMALY DETECTION SUITE")
    print("=" * 100)
    print()
    
    # Initialize Supabase client
    client = create_client(supabase_url, supabase_key)
    
    # Fetch events
    df = fetch_events_from_supabase(client, hours=48)
    
    if df.empty:
        print("No data to analyze.", file=sys.stderr)
        return 1
    
    # Run all detectors
    print("Running detection algorithms...")
    print()
    
    variance_alerts = detect_variance_escalation(df)
    print(f"✓ Variance Escalation: {len(variance_alerts)} alerts")
    
    spike_alerts = detect_spikes(df)
    print(f"✓ Spike Detection: {len(spike_alerts)} alerts")
    
    trend_alerts = detect_trends(df)
    print(f"✓ Trend Detection: {len(trend_alerts)} alerts")
    
    print()
    
    # Combine all alerts
    all_alerts = variance_alerts + spike_alerts + trend_alerts
    
    # Print report
    print_detection_report(all_alerts)
    
    # Print summary
    print_summary_statistics(df, all_alerts)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
