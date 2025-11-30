import time
import os
import logging
from prometheus_client import start_http_server, Gauge
from supabase import create_client, Client
from core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Prometheus Metrics
SCAR_SCORE = Gauge('spiralos_scar_score', 'Current ScarIndex Score')
VAULT_NODES = Gauge('spiralos_vault_nodes_total', 'Total number of VaultNodes')
ACHE_EVENTS_24H = Gauge('spiralos_ache_events_24h', 'Number of Ache events in last 24h')
GUARDIAN_ALERTS_24H = Gauge('spiralos_guardian_alerts_24h', 'Number of Guardian alerts in last 24h')
PANIC_FRAMES_ACTIVE = Gauge('spiralos_panic_frames_active', 'Number of active Panic Frames')

def fetch_metrics(supabase: Client):
    try:
        # Call the get_guardian_status RPC function
        response = supabase.rpc('get_guardian_status', {'lookback_hours': 24}).execute()
        
        if response.data:
            data = response.data
            metrics = data.get('metrics', {})
            
            SCAR_SCORE.set(data.get('scar_score', 0))
            VAULT_NODES.set(metrics.get('vault_nodes', 0))
            ACHE_EVENTS_24H.set(metrics.get('ache_events', 0))
            GUARDIAN_ALERTS_24H.set(metrics.get('alerts_24h', 0))
            PANIC_FRAMES_ACTIVE.set(metrics.get('active_panic_frames', 0))
            
            logger.info("Metrics updated", extra={"extra_data": data})
        else:
            logger.warning("No data returned from get_guardian_status")
            
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")

def main():
    # Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", 8001))
    POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 15))

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.critical("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Start Prometheus HTTP server
    start_http_server(EXPORTER_PORT)
    logger.info(f"Supabase Exporter started on port {EXPORTER_PORT}")

    while True:
        fetch_metrics(supabase)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
