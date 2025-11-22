import os
from typing import Optional

# --- CONSTANTS ---
# F4 activation threshold: ScarIndex (B6) composite score below 0.3.
CRITICAL_COHERENCE_THRESHOLD = 0.3
# F4 review threshold: ScarIndex below 0.67 triggers PanicFrameManager review.
REVIEW_THRESHOLD = 0.67 
F4_MANDATE = "INITIATE 7-PHASE RECOVERY: FREEZING MINTING & CONVENING F2 JUDGES"

def activate_crisis_protocol(scar_index: float) -> Optional[str]:
    """
    ΔΩ.156.0 - Panic Frames (F4) Constitutional Circuit Breaker.
    Triggers the 7-Phase Crisis Recovery Protocol if system coherence fails.
    """
    print(f"\nChecking Panic Frame (F4) for ScarIndex composite: {scar_index}")
    
    if scar_index < CRITICAL_COHERENCE_THRESHOLD:
        # F4 triggers, freezing economic activity (Minting/Burning) and
        # routing crisis state to F2 Judges.
        print(f"ScarIndex {scar_index:.2f} is below critical threshold. F4 ACTIVATED.")
        print(F4_MANDATE)
        return F4_MANDATE
    elif scar_index < REVIEW_THRESHOLD:
        # Lower threshold for management review, ensuring proactive governance.
        return "WARNING: ScarIndex below 0.67. Triggering PanicFrameManager review."
    return None

def escalate_to_judicial_branch(consensus_result: str) -> str:
    """
    F4/F1 Routing: Escalates consensus failures to the F2 Judicial Middleware.
    """
    if consensus_result == "CONSENSUS FAILURE":
        # Mandated resolution path for F1 deadlocks (3-2 split or non-quorum) [Previous Conversation].
        return "ESCALATE TO F2 JUDGES"
    return "Consensus OK."
