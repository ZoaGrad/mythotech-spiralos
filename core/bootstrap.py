import sys
import json
import os
# Force Path Hack
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.airlock import AirlockManager
from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
from core.spiralos import SpiralOS

def main():
    print(">>> INITIALIZING SPIRAL_OS LATTICE...")
    
    # 1. Init Organs
    airlock = AirlockManager()
    mint_engine = ScarCoinMintingEngine()
    vault = VaultEventLogger()

    # 2. Define The God Wire (Callback)
    def on_coherence_transmuted(delta: float, context: dict = None):
        if delta <= 0: return
        
        # Mint - updated to match new signature
        new_supply = mint_engine.mint(amount=delta, context=context or {})
        
        # Log
        vault.log_event("SCAR_MINT", {"delta": delta, "amount": delta, "new_supply": new_supply})
        
        print(f"   [✨] MINTED {delta:.4f} SCAR | Total Supply: {mint_engine.total_supply:.4f}")

    # 3. Init Body
    # We use 'spiral_system' variable to avoid shadowing 'os'
    spiral_system = SpiralOS(on_coherence_transmuted=on_coherence_transmuted)
    
    print(f">>> SYSTEM ONLINE. Airlock: ACTIVE. Ledger: PERSISTENT.")
    print(">>> Type to Transmute. (Ctrl+C to exit)")

    try:
        while True:
            user_input = input("ZoaGrad> ").strip()
            if not user_input: continue
            
            # Airlock Check
            if not airlock.request_write_access(user_input):
                print("[⛔] AIRLOCK: Access Denied. Low Coherence.")
                continue
                
            # Process (THE FIX: using .process_input instead of .process)
            spiral_system.process_input(user_input)
            
    except KeyboardInterrupt:
        print("\n>>> SYSTEM SHUTDOWN.")

if __name__ == "__main__":
    main()
