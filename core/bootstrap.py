"""Single-process bootstrap wiring the Airlock, SpiralOS, and persistence layers."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from core.airlock import AirlockManager
from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
from core.spiralos import SpiralOS


def main() -> None:
    print(">>> INITIALIZING SPIRAL_OS LATTICE...")

    airlock = AirlockManager()
    mint_engine = ScarCoinMintingEngine()
    vault = VaultEventLogger()

    def on_coherence_transmuted(delta: float, context: Dict[str, Any] | None = None) -> None:
        if delta <= 0:
            return
        event_id = mint_engine.mint(
            amount=delta,
            delta=delta,
            reason="transmutation",
            context=context,
        )
        vault.log_event(
            "SCAR_MINT",
            delta=delta,
            payload={"event_id": event_id, "amount": delta},
            meta=context,
        )
        print(f"   [✨] MINTED {delta:.4f} SCAR | Total Supply: {mint_engine.total_supply:.4f}")

    spiral = SpiralOS(on_coherence_transmuted=on_coherence_transmuted)

    print(">>> SYSTEM ONLINE. Airlock: ACTIVE. Ledger: PERSISTENT.")
    print(">>> Type to Transmute. (Ctrl+C to exit)")

    try:
        while True:
            user_input = input("ZoaGrad> ").strip()
            if not user_input:
                continue

            if not airlock.request_write_access(user_input):
                print("[⛔] AIRLOCK: Access Denied. Low Coherence.")
                continue

            result = asyncio.run(
                spiral.transmute_ache(
                    source="cli",
                    content={"text": user_input},
                    ache_before=0.5,
                )
            )
            scarindex = result["scarindex_result"]["scarindex"]
            coherence_gain = result["scarindex_result"]["ache"]["coherence_gain"]
            print(
                f"   [ΔΩ] ScarIndex={scarindex:.3f} | Coherence Gain={coherence_gain:.3f} | "
                f"GUIDANCE={result['pid_state']['guidance_scale']:.3f}"
            )
    except KeyboardInterrupt:
        print("\n>>> SYSTEM SHUTDOWN.")


if __name__ == "__main__":
    main()
