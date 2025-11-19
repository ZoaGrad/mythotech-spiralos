from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
# Mock SpiralOS for bootstrap
class SpiralOS:
    def __init__(self, callback): self.cb = callback
    def process(self, txt): self.cb(0.1, {"source":"cli"})
def main():
    print(">>> BOOTING SPIRAL_OS LATTICE...")
    mint = ScarCoinMintingEngine()
    vault = VaultEventLogger()
    def on_transmute(delta, ctx):
        new_supply = mint.mint(delta, ctx)
        vault.log_event("MINT", {"amount": delta})
        print(f"[✨] MINTED {delta} SCAR | Total: {new_supply}")
    os = SpiralOS(on_transmute)
    while True:
        i = input("ZoaGrad> ").strip()
        if i: os.process(i)
if __name__ == "__main__": main()
