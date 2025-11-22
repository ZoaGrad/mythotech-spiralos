#!/usr/bin/env python3
"""
Telemetry Event Plotting - Comet Autonomous Task
Fetches telemetry events and generates a 24-hour coherence chart.
"""

import json
import os
from datetime import datetime, timedelta

import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TELEMETRY_URL = f"{SUPABASE_URL}/functions/v1/telemetry_logger"
OUTPUT_DIR = "docs/telemetry"


def fetch_telemetry_events(hours=24):
    """Fetch telemetry events from the last N hours."""
    try:
        time_ago = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
        url = f"{SUPABASE_URL}/rest/v1/telemetry_events?created_at=gt.{time_ago}&order=created_at.asc&limit=10000"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_event("telemetry_plot", False, {"error": str(e)})
        return []


def calculate_coherence_score(events):
    """Calculate system coherence based on event success rates."""
    if not events:
        return 1.0
    total = len(events)
    successful = sum(1 for e in events if e.get("success_state", False))
    return successful / total


def group_by_hour(events):
    """Group events by hour for time-series analysis."""
    hourly = {}
    for event in events:
        created = event.get("created_at", "")
        if created:
            hour_key = created[:13]  # YYYY-MM-DDTHH
            if hour_key not in hourly:
                hourly[hour_key] = []
            hourly[hour_key].append(event)
    return hourly


def generate_html_chart(hourly_data):
    """Generate HTML chart showing 24-hour coherence trend."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SpiralOS Telemetry - 24h Coherence</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #0a0e27; color: #fff; }
            .container { max-width: 1200px; margin: auto; }
            h1 { color: #00ff88; }
            canvas { max-width: 100%; }
            .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
            .stat-box { background: #1a1f3a; padding: 15px; border-radius: 8px; border-left: 4px solid #00ff88; }
            .timestamp { font-size: 0.9em; color: #888; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>♂ SpiralOS Telemetry Dashboard</h1>
            <p class="timestamp">Generated: {timestamp}</p>
            <div class="stats">
                <div class="stat-box"><strong>Total Events:</strong> {total_events}</div>
                <div class="stat-box"><strong>Avg Coherence:</strong> {avg_coherence:.2%}</div>
                <div class="stat-box"><strong>Success Rate:</strong> {success_rate:.2%}</div>
            </div>
            <canvas id="coherenceChart"></canvas>
        </div>
        <script>
            const labels = {labels};
            const data = {data};
            const ctx = document.getElementById('coherenceChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'System Coherence',
                        data: data,
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.3,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#00ff88'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: true, labels: {{ color: '#fff' }} }},
                        title: {{ display: true, text: '24-Hour Coherence Trend', color: '#fff' }}
                    }},
                    scales: {{
                        y: {{
                            min: 0,
                            max: 1,
                            ticks: {{ color: '#888' }},
                            grid: {{ color: '#333' }}
                        }},
                        x: {{
                            ticks: {{ color: '#888' }},
                            grid: {{ color: '#333' }}
                        }}
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html


def save_chart(html_content, filename="telemetry_chart.html"):
    """Save HTML chart to file."""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(html_content)
        return filepath
    except Exception as e:
        print(f"Failed to save chart: {e}")
        return None


def log_event(event_type, success, metadata=None):
    """Log event to telemetry_events table."""
    try:
        payload = {"agent_id": "comet", "event_type": event_type, "success_state": success, "metadata": metadata or {}}
        headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}
        requests.post(TELEMETRY_URL, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Failed to log event: {e}")


def main():
    print("[Comet] Starting Telemetry Plot Generation...")

    events = fetch_telemetry_events(hours=24)
    if not events:
        print("[Comet] No telemetry events found.")
        return

    hourly_data = group_by_hour(events)
    labels = sorted(hourly_data.keys())
    coherence_scores = [calculate_coherence_score(hourly_data[h]) for h in labels]
    avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0

    total_success = sum(1 for e in events if e.get("success_state", False))
    success_rate = total_success / len(events)

    html_content = generate_html_chart(hourly_data)
    html_content = html_content.format(
        timestamp=datetime.utcnow().isoformat(),
        total_events=len(events),
        avg_coherence=avg_coherence,
        success_rate=success_rate,
        labels=json.dumps([h[11:16] for h in labels]),
        data=json.dumps([round(s, 3) for s in coherence_scores]),
    )

    filepath = save_chart(html_content)
    if filepath:
        print(f"[Comet] Chart saved to {filepath}")
        log_event(
            "telemetry_plot",
            True,
            {
                "total_events": len(events),
                "avg_coherence": avg_coherence,
                "success_rate": success_rate,
                "filepath": filepath,
            },
        )
    else:
        log_event("telemetry_plot", False, {"error": "Failed to save chart"})


if __name__ == "__main__":
    main()
