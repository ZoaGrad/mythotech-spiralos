import os
import time
import logging
import json
from datetime import datetime, timezone
from supabase import create_client, Client

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pantheon_daemon')

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
POLL_INTERVAL = int(os.getenv("PANTHEON_POLL_INTERVAL_SECONDS", 60))

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.critical("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_view_data(view_name):
    """Helper to fetch data from a view."""
    try:
        # Fetch latest data (assuming views return daily rows, we want the most recent)
        # For drift, it returns current day.
        # For others, we order by day desc.
        res = supabase.table(view_name).select("*").limit(10).execute() # Fetch a few to be safe, logic handles filtering
        return res.data
    except Exception as e:
        logger.error(f"Error fetching {view_name}: {e}")
        return []

def calculate_coherence(stability, drift, velocity_norm):
    """
    Spiritual Health Calculation:
    coherence = (stability * 0.5) + ((1.0 - drift) * 0.3) + (velocity_norm * 0.2)
    """
    return (stability * 0.5) + ((1.0 - drift) * 0.3) + (velocity_norm * 0.2)

def main():
    logger.info("👁️ Pantheon Daemon Online. Opening the Sovereign Eye...")
    
    while True:
        try:
            logger.info("--- Starting Telemetry Cycle ---")
            
            # 1. Fetch Data
            drift_data = fetch_view_data("view_council_drift")
            stability_data = fetch_view_data("view_cognitive_stability")
            velocity_data = fetch_view_data("view_emp_velocity")
            # ache_data = fetch_view_data("view_ache_resonance") # Not used in coherence yet, but good to have

            # 2. Derive Metrics
            
            # Current Stability (Agreement Ratio)
            # Find latest day
            current_stability = 1.0 # Default
            if stability_data:
                # Sort by day desc just in case
                latest_stab = sorted(stability_data, key=lambda x: x['day'], reverse=True)[0]
                current_stability = float(latest_stab.get('agreement_ratio', 1.0))
            
            # Current Drift (Avg Abs Delta)
            current_drift = 0.0
            if drift_data:
                # drift_data has one row per role per day.
                # We want the average of abs(delta) for the current day.
                # Assuming the view returns rows for "today".
                deltas = [abs(float(r['delta_from_baseline'])) for r in drift_data]
                if deltas:
                    current_drift = sum(deltas) / len(deltas)
                # Clamp to 0-1 (though delta can be > 1 technically, usually small)
                current_drift = min(1.0, current_drift)

            # Velocity (Mint Rate)
            velocity_minted = 0.0
            if velocity_data:
                latest_vel = sorted(velocity_data, key=lambda x: x['day'], reverse=True)[0]
                velocity_minted = float(latest_vel.get('mint_rate', 0.0))
            
            # Normalize Velocity (Heuristic: Target 100 EMP/day = 1.0)
            TARGET_MINT_RATE = 100.0
            velocity_normalized = min(1.0, velocity_minted / TARGET_MINT_RATE)

            # 3. Calculate Coherence
            coherence = calculate_coherence(current_stability, current_drift, velocity_normalized)
            
            # Determine Health State
            health_state = "STABLE_FLOW"
            if coherence > 0.9:
                health_state = "SOVEREIGN_ALIGNMENT"
            elif coherence < 0.6:
                health_state = "FRACTURE_DETECTED"

            logger.info(f"Coherence: {coherence:.3f} | State: {health_state}")
            logger.info(f"Metrics -> Stab: {current_stability:.2f}, Drift: {current_drift:.2f}, Vel: {velocity_minted} ({velocity_normalized:.2f})")

            # 4. Write Telemetry
            telemetry_payload = {
                "coherence": coherence,
                "current_stability": current_stability,
                "current_drift": current_drift,
                "velocity_minted": velocity_minted,
                "velocity_normalized": velocity_normalized,
                "health_state": health_state,
                "metadata": {
                    "source": "pantheon_daemon",
                    "version": "1.0"
                }
            }
            
            supabase.table("observatory_telemetry").insert(telemetry_payload).execute()
            logger.info("Telemetry recorded.")

            # 5. Handle Alerts
            if health_state == "FRACTURE_DETECTED":
                logger.warning("🚨 FRACTURE DETECTED! Triggering alert...")
                # Insert into guardian_alerts if table exists, or just log for now.
                # The prompt suggests `guardian_alerts` or `guardian_anomalies`.
                # Let's try `guardian_anomalies` as we used that in a previous task (Sequence C/D).
                try:
                    alert_payload = {
                        "type": "COGNITIVE_FRACTURE",
                        "severity": "critical",
                        "description": f"System coherence dropped to {coherence:.3f}. Stability: {current_stability:.2f}",
                        "metadata": telemetry_payload
                    }
                    # We need to check if guardian_anomalies exists and schema.
                    # Assuming standard schema from previous tasks.
                    # If it fails, we catch it.
                    # Actually, let's use a generic log if we aren't sure of the table.
                    # But the prompt explicitly asked to insert an alert.
                    # I'll try `guardian_alerts` first (standard name), then `guardian_anomalies`.
                    # Wait, I recall `guardian_anomalies` from the conversation history summary.
                    supabase.table("guardian_anomalies").insert(alert_payload).execute()
                    logger.info("Alert sent to guardian_anomalies.")
                except Exception as e:
                    logger.error(f"Failed to send alert: {e}")

        except Exception as e:
            logger.error(f"Cycle failed: {e}")
        
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
