import asyncio
import json
import time

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

        # Mint
        ctx_json = json.dumps(context or {})
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
            try:
                asyncio.run(
                    spiral.transmute_ache(
                        source="bootstrap_cli",
                        content={"input": user_input, "ts": time.time()},
                        ache_before=0.8,
                    )
                )
            except Exception as exc:  # pragma: no cover - operator diagnostic output
                print(f"[!] SpiralOS processing error: {exc}")

    except KeyboardInterrupt:
        print("\n>>> SYSTEM SHUTDOWN.")

if __name__ == "__main__":
    main()
