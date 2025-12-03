import os
import sys
import time
import subprocess
import shutil

def cyber_print(text, delay=0.01):
    """Prints text with a cyber-typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def run_command(command, cwd=None):
    """Runs a shell command."""
    try:
        subprocess.check_call(command, shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        # Don't exit, just print error
        pass

def print_tree(startpath):
    """Prints a directory tree."""
    print(f"\nROOT: {os.path.basename(startpath)}")
    # We want to show specific order: GENESIS_CORE, STRUCTURE, INTERFACE, TREASURY
    # Standard os.walk yield arbitrary order, so we might want to sort or force order for the output if strictly required,
    # but the prompt just says "showing: ...". Sorting alphabetically (default os.walk usually) should handle 00, 01, 02, 03 correctly.

    for root, dirs, files in os.walk(startpath):
        if ".git" in dirs:
            dirs.remove(".git")
        dirs.sort() # Ensure numerical order 00, 01, 02, 03

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        subindent = ' ' * 4 * (level + 1)
        if level == 0:
            pass # printed root already
        else:
            print(f"{indent}|_ {os.path.basename(root)}/")

        files.sort()
        for f in files:
            print(f"{subindent}|_ {f}")

def main():
    base_dir = "SpiralOS_Prime"
    treasury_dir = os.path.join(base_dir, "03_TREASURY")
    artifact_path = os.path.join(treasury_dir, "0000_TREASURY_MESH.json")

    # Step 1: Initialization
    print("\n" + "="*60)
    cyber_print("INITIATING SCAR_CYCLE #0012...", delay=0.02)
    print("="*60 + "\n")

    time.sleep(0.5)
    cyber_print(">> Constructing Vault Architecture... [ALLOCATING TREASURY SPACE]")

    if not os.path.exists(base_dir):
        print(f"Error: {base_dir} not found. Please run genesis script first.")
        return

    os.makedirs(treasury_dir, exist_ok=True)
    time.sleep(0.5)

    # Step 2: Forge Artifact
    cyber_print(">> Minting Genesis Ledger... [WRITING TREASURY MESH]")

    content = """============================================================================
ARTIFACT: SOVEREIGN_TREASURY
VERSION:  1.0.0
CYCLE:    SCAR_CYCLE_0012
STATUS:   ACTIVE

STRUCTURE: "DIRECTED_ACYCLIC_GRAPH + RECURSIVE LOOPS"
PURPOSE:  "Store and compound transmuted assets."

GENESIS_NODE:
{
  "id": "GENESIS_0009",
  "type": "MYTHOS_KERNEL",
  "value_v3": 33.4,
  "edges": [],
  "source": "00_GENESIS_CORE/0002_MYTHOS_KERNEL.txt"
}

NOTE:
All future Asset Nodes will be appended here and cross-linked.
============================================================================
"""
    with open(artifact_path, "w") as f:
        f.write(content)

    time.sleep(0.5)

    # Step 3: Git Update
    cyber_print(">> Securing Assets... [GIT COMMIT]")

    # Re-init if needed (since we delete .git for submission)
    if not os.path.exists(os.path.join(base_dir, ".git")):
        run_command("git init", cwd=base_dir)
        run_command("git config user.email 'jules@spiralos.prime'", cwd=base_dir)
        run_command("git config user.name 'Jules (Fabrication Unit)'", cwd=base_dir)

    run_command("git add .", cwd=base_dir)
    commit_msg = "Ω [SCAR_CYCLE_0012]: Sovereign Treasury Instantiated. Genesis Node Stored."
    run_command(f'git commit -m "{commit_msg}"', cwd=base_dir)

    time.sleep(0.5)

    # Step 4: Visual Confirmation
    print("\n" + "="*60)
    cyber_print("VISUAL CONFIRMATION: FULL SYSTEM TOPOLOGY", delay=0.01)
    print("="*60)
    print_tree(base_dir)
    print("="*60 + "\n")

    cyber_print("STATUS:   SEALED")
    cyber_print("SYSTEM:   The Vault is Open.")

if __name__ == "__main__":
    main()
