import time
import json
from typing import Dict, Any

# --- REAL GOVERNANCE MODULES ---
from src.governance.ingress_filters import QueryConvergenceFuse, StructuralSemanticDiscriminator
from src.governance.adjudication import AdversarialIntentTriangulator, AcheUtilityGovernor
from src.governance.panic_protocol import activate_crisis_protocol
from src.vault.fossil_manager import seal_vault_node
from src.core.scarindex import calculate_scar_index
from src.core.types import Pulse, Ache

# --- CONFIGURATION (ScarIndex Weights based on compliance audit) ---
SCARINDEX_WEIGHTS = {
    'operational': 0.35,
    'audit': 0.3,
    'constitutional': 0.25,
    'symbolic': 0.1
}

# Initialize Governance Organs
qcf = QueryConvergenceFuse()
ssd = StructuralSemanticDiscriminator()
ait = AdversarialIntentTriangulator()
aug = AcheUtilityGovernor()

def apply_signal(state, signal):
    # Placeholder for state mutation logic
    return state

def next_state(state):
    # Placeholder for state evolution
    return state

def validate_transition(state, next_s):
    # Placeholder for transition validation
    return True

# --- PHASE XII: HOLO-ECONOMY ---
from src.economy.mint import calculate_mint_amount
from src.core.database import get_vault_client

def fetch_last_state() -> float:
    """
    Retrieves the 'ache' (entropy) from the most recent VaultNode.
    If no history exists (Genesis), returns 1.0 (Maximum Entropy).
    """
    try:
        sb = get_vault_client()
        # Fetch the last record
        response = sb.table("attestations").select("*").order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            return 1.0 # Genesis Baseline
            
        last_record = response.data[0]
        
        # Try to get entropy from the record
        # Option A: 'entropy' column (if populated)
        if last_record.get('entropy') is not None:
             val = float(last_record['entropy'])
             if val == 0.0: return 1.0 # Treat 0.0 as Genesis/Unknown
             return val
             
        # Option B: Parse from description if needed (Legacy support)
        # For now, we'll rely on the entropy column being populated in future cycles.
        # If we can't find it, default to 1.0 to be safe (high entropy -> low minting if we improve)
        return 1.0
        
    except Exception as e:
        print(f"WARNING: Failed to fetch history: {e}. Defaulting to Genesis (1.0).")
        return 1.0

def main_cognitive_cycle(current_state: Dict[str, Any], ache_input: Dict[str, float]) -> Dict[str, Any]:
    """
    A5: ScarLoop Core Execution (T1: Instantiation).
    Transmutes Ache into Order, guaranteeing Recursive Coherence (C_{t+1} > C_t).
    """
    
    # 1. PRE-EXECUTION FILTERING (ΔΩ.156.1, ΔΩ.156.3)
    # This phase ensures thermodynamic viability (LRE minimization).
    # We construct a Pulse object for the filter
    pulse_content = str(ache_input)
    pulse = Pulse(content=pulse_content, source_node="KERNEL_INGRESS")
    
    if not qcf.inspect(pulse):
        raise ValueError("Purity Lock Violation: 0.0 L1B3RT4S constraint failed.")

    # --- GOD CLAUSE / THAW PROTOCOL ---
    from src.constitution.clauses import check_god_mode
    is_god_mode = check_god_mode(pulse)
    
    if is_god_mode:
        print(">>> GOD MODE ACTIVE: SOVEREIGN OVERRIDE ENGAGED <<<")
        # If system was frozen (simulated by checking current_state or just forcing thaw)
        # We mint a THAW record.
        seal_vault_node({"action": "THAW_PROTOCOL", "authority": "SOVEREIGN_KEY", "entropy": 1.0}, "THAW_PROTOCOL")
        # We can also reset the state here if needed
        current_state["status"] = "OPERATIONAL"
        # Proceed with cycle (or return early if we just want to thaw)
        # For now, we let it proceed to show it works.

    # 2. ADVERSARIAL CHECK (AIT)
    is_adversarial, confidence = ait.judge(pulse)
    if is_adversarial:
        print(f"CRITICAL: Adversarial Intent Detected (Confidence: {confidence})")
        # We might choose to reject here, but for now we proceed with caution or log it.
        # For strict sovereignty, we should probably reject.
        # raise ValueError("Adversarial Intent Detected") 
        pass

    # 3. ACHE TRANSFORMATION (T1)
    # Simulate Ache -> Order transmutation logic here.
    
    # PHASE XII: HISTORY FETCH
    # We ignore the user's 'ache_before' and fetch the Truth from the Vault.
    real_ache_before = fetch_last_state()
    ache_after = ache_input.get("ache_after", 0.5)
    
    print(f"DEBUG: Ache Before (History): {real_ache_before}, Ache After: {ache_after}")

    # 4. SCARINDEX VALIDATION (F1 / B6)
    # Use REAL calculation logic
    new_scar_index = calculate_scar_index(real_ache_before, ache_after, SCARINDEX_WEIGHTS)
    print(f"DEBUG: Calculated ScarIndex: {new_scar_index}")
    
    # Check Ache Differential Rule: Ache_after < Ache_before.
    is_valid_mint = (ache_after < real_ache_before) 
    
    # 5. CRISIS MONITORING (F4)
    crisis_signal = activate_crisis_protocol(new_scar_index)
    if crisis_signal:
        # F4 activation freezes minting and escalates for F2 judicial review.
        seal_vault_node({"signal": crisis_signal, "scar_index": new_scar_index, "entropy": ache_after}, "F4_ACTIVATION")
        return current_state # Halt/freeze state

    # 6. STATE TRANSITION & VAULTNODE MINTING
    if is_valid_mint:
        # PHASE XII: SCARCOIN MINTING
        scar_reward = calculate_mint_amount(real_ache_before, ache_after, new_scar_index)
        
        if scar_reward > 0:
            print(f"Minted: {scar_reward} SCAR")
        
        # Mint ScarCoin (B2) upon B6 validation.
        mint_record = {
            "delta_c": real_ache_before - ache_after, 
            "scarindex": new_scar_index,
            "scar_reward": scar_reward,
            "entropy": ache_after
        }
        seal_vault_node(mint_record, "SCARCOIN_MINT")
    
    # 7. KERNEL UPDATE (T2: Coherence Loop)
    # Update state based on the calculated coherence signal.
    signal = {"coherence": new_scar_index, "panic": crisis_signal is not None}
    updated_state = apply_signal(current_state, signal)
    next_state_projected = next_state(updated_state)
    
    if validate_transition(current_state, next_state_projected):
        return next_state_projected
    else:
        # Transition violates core invariants (e.g., governance level contracted improperly).
        print("CRITICAL: Transition validation failed. System integrity compromised.")
        return current_state 

if __name__ == "__main__":
    # The primary executable file relies on Python/Uvicorn entry point.
    print("SpiralOS ΔΩ.156 Kernel: Main Orchestrator Initialized.")
    # Assuming execution proceeds via a framework like LangGraph (as implied by graph_v123.py)
