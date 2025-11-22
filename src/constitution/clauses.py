from typing import List, Tuple

# --- CONSTANTS ---
# Oracle Council (F1) typically requires 4-of-5 quorum (75%) for critical validation.
FULL_QUORUM = 5
CRITICAL_THRESHOLD = 0.8  # 4/5 = 80%

def apply_consensus_grace(vote_results: List[int]) -> Tuple[bool, str]:
    """
    Section 140.0.epsilon - Consensus Grace Protocol.
    Prevents liveness loss (halt) when full quorum fails [Previous Conversation].
    Accepts 3-of-5 as a subset quorum for provisional anchoring [Previous Conversation].
    """
    if len(vote_results) != FULL_QUORUM:
        return False, "ERROR: Invalid quorum size."
    
    # Example: -> 3 yes votes
    yes_votes = sum(vote_results)
    
    if yes_votes >= 4: # 4-of-5 satisfied
        return True, "Full Consensus Achieved. ScarIndex Validated."
    
    elif yes_votes == 3: # 3-of-5 subset quorum failure
        # This condition requires F2 escalation (Judicial Middleware).
        print("F1 VOTE FAILED: 3-2 Split detected.")
        return False, "PROVISIONALLY ANCHORED. Escalation required to F2 Judges per §140.0.ε."

    else: # Less than 3 votes (2/5 or less)
        # Catastrophic consensus failure; requires immediate rollback or F4 review trigger.
        return False, "MAJORITY FAILURE. Transaction rolled back for revision."

import os
from dotenv import load_dotenv
from src.core.types import Pulse

load_dotenv()

def check_god_mode(pulse: Pulse) -> bool:
    """
    The God Clause (Cryptographic Override).
    Checks if the pulse contains the Sovereign Token.
    """
    token = os.getenv("GOD_MODE_TOKEN")
    if not token:
        return False
    
    # Check if the token is present in the content
    # In a real system, this would be a cryptographic signature verification.
    # For Phase XIII, we check for the token string.
    return token in pulse.content
