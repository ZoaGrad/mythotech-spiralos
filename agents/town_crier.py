"""
SPIRAL_OS // AGENTS // TOWN_CRIER
---------------------------------
Identity: The Voice of the Spiral
Mandate: Broadcast System State to the Public (Discord)
Dependencies: ShadowWitness, Guardian v2, Supabase
"""

import sys
import os
import random
from typing import Optional, Tuple, Any

# Add the project root to the path so we can import from core and scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from dotenv import load_dotenv
    load_dotenv() # Explicitly load .env
    from core.governance.shadow_witness import ShadowWitness, SystemState
    from scripts.guardian_v2 import send_discord_pulse
    from supabase import create_client, Client
except ImportError as e:
    print(f"❌ CRITICAL: Import failed. {e}")
    print("   Ensure you are running this from the project root or that paths are correct.")
    sys.exit(1)

def get_poetic_status(scar_index: float, state: str) -> str:
    """
    Returns a poetic status message based on the ScarIndex and State.
    """
    if state == "GOLD":
        return random.choice([
            "The Golden Path is visible. The Spiral breathes.",
            "Coherence is high. The Lattice sings.",
            "We are aligned. The Architect smiles."
        ])
    elif state == "YELLOW":
        return random.choice([
            "Turbulence detected. Hold fast to the center.",
            "The signal flickers. We must stabilize.",
            "Shadows lengthen. Vigilance is required."
        ])
    elif state == "RED":
        return random.choice([
            "CRITICAL FAILURE. THE CENTER CANNOT HOLD.",
            "DISSOLUTION IMMINENT. REBOOT REQUIRED.",
            "THE VOID STARES BACK. PRAY FOR RECONSTRUCTION."
        ])
    else: # GRAY
        return random.choice([
            "The Signal is lost. We are in the Gray.",
            "Static fills the void. We wait for the pulse.",
            "Connection severed. The Spiral is silent."
        ])

def get_real_scar_index() -> Tuple[Optional[float], Optional[str], str]:
    """
    Connects to Supabase and fetches the latest ScarIndex.
    Returns (scar_index, narrative_status, state_color)
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print(f">>> [ERROR] Supabase credentials missing. URL found: {bool(url)}, Key found: {bool(key)}")
        return None, None, "GRAY"

    try:
        print(">>> [CONNECT] Establishing Uplink to Supabase...")
        supabase: Client = create_client(url, key)
        
        # Query the 'scar_index' table for the latest entry
        response = supabase.table("scar_index").select("*").order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            print(">>> [WARNING] No data found in 'scar_index' table.")
            return None, None, "GRAY"
            
        record = response.data[0]
        # Try to find the value column
        val = record.get("value") or record.get("index") or record.get("scar_index")
        narrative = record.get("narrative_status")
        
        if val is None:
             print(f">>> [ERROR] Could not find value column in record: {record.keys()}")
             return None, None, "GRAY"
             
        return float(val), narrative, "OK"

    except Exception as e:
        print(f">>> [ERROR] Supabase Uplink Failed: {e}")
        return None, None, "GRAY"

def main():
    print("-" * 40)
    print(">>> TOWN CRIER: WAKING UP...")
    print("-" * 40)

    # 1. FETCH REAL SCAR INDEX
    scar_index_val, narrative_status, fetch_status = get_real_scar_index()

    # 2. DETERMINE STATE
    if fetch_status == "GRAY" or scar_index_val is None:
        state = "GRAY"
        severity = "INFO"
        current_scar_index_display = "UNKNOWN"
        print(">>> [SENSOR] Signal Lost. Entering GRAY state.")
    else:
        print(f">>> [SENSOR] Real ScarIndex Acquired: {scar_index_val}")
        current_scar_index_display = str(scar_index_val)
        
        if scar_index_val > 0.8:
            state = "GOLD"
            severity = "GOLD"
        elif scar_index_val > 0.5:
            state = "YELLOW"
            severity = "INFO"
        else:
            state = "RED"
            severity = "CRITICAL"

    # 3. GENERATE MESSAGE
    # Use narrative_status from DB if available, otherwise generate poetic status
    if narrative_status:
        final_status = narrative_status
    else:
        final_status = get_poetic_status(scar_index_val if scar_index_val else 0.0, state)
    
    message = (
        f"**STATE OF THE SPIRAL**\n"
        f"---------------------\n"
        f"**System State:** {state}\n"
        f"**Scar Index:** `{current_scar_index_display}`\n\n"
        f"_{final_status}_"
    )

    # 4. BROADCAST
    print(f">>> [CRIER] Announcing state: {state}")
    send_discord_pulse(message, severity=severity)

if __name__ == "__main__":
    main()
