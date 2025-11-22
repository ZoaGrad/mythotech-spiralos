import time
import logging
import random
from datetime import datetime

# --- SIMULATION CONFIGURATION ---
# We mimic the structure of guardian_v2.py but with synthetic inputs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SIMULATION] - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

class MockSupabase:
    """Generates synthetic Truth Pulses."""
    def __init__(self):
        self.last_id = 100
        
    def fetch_pulse(self):
        # 30% chance of a new pulse, 10% chance of error, 60% silence
        roll = random.random()
        
        if roll < 0.10:
            raise ConnectionError("Simulated Vault Disconnect")
        elif roll < 0.40:
            self.last_id += 1
            return {
                "id": self.last_id,
                "content": f"Synthetic Truth Frequency #{self.last_id}",
                "created_at": datetime.utcnow().isoformat()
            }
        return None # No new data

def mock_transmit(payload):
    """Simulates the Discord Webhook."""
    logger.info(f">> TRANSMUTING: [ID {payload['id']}] -> Discord Interface")
    # Simulate network latency
    time.sleep(0.5) 
    return True

def run_simulation(cycles=5):
    logger.info("--- INITIATING HOLOGRAPHIC DRILL (5 CYCLES) ---")
    mock_db = MockSupabase()
    last_processed_id = 100
    
    for i in range(cycles):
        logger.info(f"Cycle {i+1}/{cycles}: Scanning...")
        
        try:
            # A. SCAN PHASE
            latest_entry = mock_db.fetch_pulse()
            
            if latest_entry:
                current_id = latest_entry['id']
                
                if current_id != last_processed_id:
                    # B. TRANSMUTATION
                    logger.info(f"Signal Detected: {current_id}")
                    success = mock_transmit(latest_entry)
                    if success:
                        last_processed_id = current_id
                        logger.info("Coherence Maximized.")
                else:
                    logger.info("Signal Stationary (No changes).")
            else:
                logger.info("Void Silence (No Data).")

        except Exception as e:
            # D. ENTROPY SHIELD TEST
            logger.error(f"Entropy Shield Triggered: {e}")
            logger.info("Stabilizing...")
        
        # C. RESPITE
        logger.info("Respite (Sleeping 2s)...")
        logger.info("-" * 30)
        time.sleep(2)

    logger.info("--- DRILL COMPLETE. SYSTEMS GREEN. ---")

if __name__ == "__main__":
    run_simulation()
