import time
import logging
import os
from datetime import datetime, timezone
from core.scarindex import scar_index
from core.soc_pid_controller import SOCPIDController
from core.db import get_supabase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coherence_loop")

def run_coherence_cycle():
    """
    Executes one cycle of the Coherence Core:
    1. Compute ScarIndex from recent telemetry.
    2. Feed ScarIndex into SOC PID Controller.
    3. PID Controller persists Ache/SoC signals.
    """
    logger.info("Starting Coherence Cycle...")
    
    # 1. Compute ScarIndex
    # We use a 5-minute window by default
    current_scarindex = scar_index.compute_scarindex_for_window(minutes=5)
    logger.info(f"Computed ScarIndex: {current_scarindex}")
    
    # 2. Update PID Controller
    # Initialize controller (in a real app, this would be persistent or loaded from DB state)
    # For this runner, we instantiate it fresh, which is fine for stateless/stateless-ish updates
    # provided we don't need integral history across *process* restarts for this simple test.
    # In a real daemon, we'd keep the instance alive.
    controller = SOCPIDController()
    
    # We need a proxy for "event size" for SOC. 
    # We can estimate it from the number of telemetry events in the window.
    # Ideally ScarIndex would return this metadata.
    # Let's fetch the last signal to get event count.
    supabase = get_supabase()
    res = supabase.table("coherence_signals").select("*").order("timestamp", desc=True).limit(1).execute()
    
    event_size = 1.0
    if res.data:
        last_signal = res.data[0]
        if "signal_data" in last_signal and "event_count" in last_signal["signal_data"]:
            event_size = float(last_signal["signal_data"]["event_count"])
    
    guidance, status = controller.update_soc(current_scarindex, event_size)
    logger.info(f"PID Update Complete. Guidance: {guidance:.4f}")
    logger.info(f"SOC Status: {status['soc_metrics']['is_critical']}")

if __name__ == "__main__":
    try:
        run_coherence_cycle()
        logger.info("Cycle completed successfully.")
    except Exception as e:
        logger.error(f"Cycle failed: {e}")
        exit(1)
