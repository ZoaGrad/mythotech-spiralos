import sys
import os

# Ensure python can find the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import main_cognitive_cycle
from src.core.types import ScarIndex # Assuming types are available, or we mock if needed
from typing import Dict, Any

# --- MOCK STATE ---
genesis_state = {
    "epoch": 1,
    "entropy": 0.5,
    "governance_layer": "L1"
}

# --- SCENARIO A: THE HEALTHY BREATH ---
# Ache decreases (Thermodynamic Success)
healthy_pulse = {
    "ache_before": 1.0,
    "ache_after": 0.8 # Decrease = Valid
}

# --- SCENARIO B: THE PANIC TRIGGER ---
# Ache increases or triggers low ScarIndex (Thermodynamic Failure/Crisis)
# We simulate a result that causes low ScarIndex calculation
panic_pulse = {
    "ache_before": 0.5,
    "ache_after": 0.9 # Increase = Disorder = Low ScarIndex
}

def run_ignition():
    print("\n>>> DO.156 IGNITION SEQUENCE INITIATED <<<\n")

    # 1. Test Healthy Cycle
    print("--- [TEST 1] HEALTHY TRANSITION ---")
    try:
        next_state = main_cognitive_cycle(genesis_state, healthy_pulse)
        print(f"SUCCESS: State evolved to Epoch {next_state.get('epoch', '?')}")
        print("System Status: NOMINAL (Green)")
    except Exception as e:
        print(f"FAILURE: {e}")

    print("\n" + "="*30 + "\n")

    # 2. Test Panic Cycle (F4)
    print("--- [TEST 2] F4 PANIC TRIGGER ---")
    try:
        # Note: main_cognitive_cycle uses a mock calculate_scar_index in main.py
        # which returns 0.20 if ache_after > ache_before. 
        # 0.20 is < 0.3 (CRITICAL THRESHOLD).
        result = main_cognitive_cycle(genesis_state, panic_pulse)
        print(f"RESULT: {result}")
    except Exception as e:
        print(f"EXCEPTION CAUGHT (Expected if Halt): {e}")

    print("\n" + "="*30 + "\n")

    # 3. Test Thaw Protocol (God Mode)
    print("--- [TEST 3] THAW PROTOCOL (GOD MODE) ---")
    
    # Simulate a Frozen State
    frozen_state = {"epoch": 1, "entropy": 0.5, "governance_layer": "L1", "status": "FROZEN"}
    
    # Input with God Token
    # We need to load the token from .env to match what the system expects
    import os
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("GOD_MODE_TOKEN")
    
    thaw_input = {
        "ache_before": 1.0, 
        "ache_after": 0.9, # Would normally trigger panic (entropy increase)
        "god_token": token # Inject token into payload string representation
    }
    
    print(f"Injecting God Token: {token}")
    
    # We need to make sure the token ends up in the pulse content.
    # main.py does: pulse_content = str(ache_input)
    # So having it in the dict is enough.
    
    try:
        result_thaw = main_cognitive_cycle(frozen_state, thaw_input)
        print("SUCCESS: System Thawed/Overridden.")
        print("Result State:", result_thaw)
    except Exception as e:
        print(f"FAILURE: God Mode Rejected. {e}")

    print("\n" + "="*30 + "\n")

    # 4. Test Minting Protocol (Phase XII)
    print("--- [TEST 4] MINTING PROTOCOL (SCARCOIN) ---")
    
    # We need to simulate a state where history exists.
    # Since main.py fetches from Supabase, and we just ran tests that inserted data,
    # we should have a history.
    # The last test (Thaw) inserted a THAW record.
    # Let's try to improve upon that.
    # Note: fetch_last_state might return 1.0 if it can't parse entropy.
    # If it returns 1.0, and we input 0.5, we have Delta C = 0.5.
    # ScarIndex should be high.
    # Mint = 0.5 * ScarIndex * 10.
    
    mint_pulse = {
        "ache_after": 0.5 # Significant improvement from 1.0 (default) or whatever is in DB
    }
    
    try:
        # We don't pass ache_before anymore, main.py fetches it.
        result_mint = main_cognitive_cycle(genesis_state, mint_pulse)
        print("SUCCESS: Cycle Complete.")
        # We check logs for "Minted: ... SCAR"
    except Exception as e:
        print(f"FAILURE: Minting Cycle Failed. {e}")

    print("\n>>> IGNITION SEQUENCE COMPLETE <<<")

if __name__ == "__main__":
    run_ignition()
