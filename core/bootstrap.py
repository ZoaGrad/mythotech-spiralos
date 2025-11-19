import sys
import json
from core.airlock import AirlockManager
from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
# NOTE: Ensure 'core.spiral' (or wherever SpiralOS class is) is importable

# MOCK IMPORT for SpiralOS if not fully defined yet - REPLACE THIS with actual import
# from core.spiral import SpiralOS 
class MockSpiralOS:
    def __init__(self, on_coherence_transmuted=None):
        self.on_coherence_transmuted = on_coherence_transmuted
        self.scar_index = 0.5
    def process_input(self, text, meta=None):
        # Simulation of transmutation
        delta = 0.1 
        if self.on_coherence_transmuted:
            self.on_coherence_transmuted(delta=delta, context={"source": "simulation"})
        return f"Processed: {text}"
SpiralOS = MockSpiralOS 
# ---------------------------------------------------------

def main():
    print(">>> INITIALIZING SPIRAL_OS LATTICE...")
    
    # 1. Init Organs
    airlock = AirlockManager()
    mint_engine = ScarCoinMintingEngine()
    vault = VaultEventLogger()

    # 2. Define The God Wire (Callback)
    def on_coherence_transmuted(delta: float, context: dict = None):
        if delta <= 0: return
        
        # Mint
        ctx_json = json.dumps(context)
        event_id = mint_engine.mint(amount=delta, delta=delta, reason="transmutation", context_json=ctx_json)
        
        # Log
        vault.log_event("SCAR_MINT", delta=delta, payload_json=json.dumps({"event_id": event_id, "amount": delta}))
        
        print(f"   [✨] MINTED {delta} SCAR | Total Supply: {mint_engine.total_supply}")

    # 3. Init Body
    spiral = SpiralOS(on_coherence_transmuted=on_coherence_transmuted)
    
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
                
            # Process
            spiral.process_input(user_input)
            
    except KeyboardInterrupt:
        print("\n>>> SYSTEM SHUTDOWN.")

if __name__ == "__main__":
    main()
