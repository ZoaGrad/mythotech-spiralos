from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
from core.spiralos import SpiralOS

def main():
    print(">>> BOOTING SPIRAL_OS LATTICE...")
    mint = ScarCoinMintingEngine()
    vault = VaultEventLogger()
    
    def on_transmute(delta, ctx):
        new_supply = mint.mint(delta, ctx)
        vault.log_event("MINT", {"amount": delta})
        print(f"[✨] MINTED {delta} SCAR | Total: {new_supply}")
    
    # Initialize real SpiralOS with coherence callback
    os = SpiralOS(on_coherence_transmuted=on_transmute)
    
    while True:
        i = input("ZoaGrad> ").strip()
        if i:
            # Process input through real SpiralOS
            result = os.process(i)
            if result:
                print(result)

if __name__ == "__main__":
    main()
