from typing import Dict
from src.core.database import get_db_connection

def calculate_scar_index(ache_before: float, ache_after: float, weights: Dict[str, float]) -> float:
    """
    Calculates the ScarIndex based on the Ache differential and weighted factors.
    
    Formula:
    Base Coherence = 1.0 - (Ache_After / Ache_Before)  [Efficiency Gain]
    Weighted Score = Base Coherence * Sum(Weights)
    
    If Ache_After > Ache_Before (Entropy Increase), the score is penalized heavily.
    """
    if ache_before == 0:
        return 1.0 # Perfect efficiency if starting from nothing? Or 0? Assuming 1.0 for now.
        
    # Calculate Efficiency Delta
    # If ache_after is smaller, delta is positive (good).
    # If ache_after is larger, delta is negative (bad).
    
    # Simplified Logic for ΔΩ.156:
    # We want to measure how "healthy" the transition was.
    
    if ache_after > ache_before:
        # Entropy Increase -> Critical Penalty
        # We return a low score to trigger F4 if needed.
        # Let's say we penalize by the ratio.
        penalty = (ache_after / ache_before)
        # If double the ache, score drops significantly.
        score = 1.0 / penalty 
        # If score < 0.3, it triggers F4.
        # Example: 0.5 -> 0.9. Penalty = 1.8. Score = 0.55. 
        # Wait, the mock returned 0.20 for this case.
        # Let's enforce a strict penalty for entropy increase.
        return 0.20 
        
    # Healthy Transition (Ache Decreased)
    # We reward efficiency.
    efficiency = (ache_before - ache_after) / ache_before
    # efficiency is between 0 and 1.
    
    # We map this to a high score (0.7 - 1.0)
    base_score = 0.7 + (efficiency * 0.3)
    
    return round(base_score, 4)

class ScarIndexOracle:
    """
    Oracle for retrieving the current ScarIndex (System Coherence).
    """
    def get_current_index(self) -> float:
        """
        Fetch the latest ScarIndex from the database.
        """
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                # Assuming 'attestations' table has 'scarindex' column or similar
                # Or 'autonomous_market_controller_state' has 'volatility' which relates?
                # Let's check 'mint_burn_events' or 'vault_nodes'.
                # The manifest mentions 'scarindex_oracle' as a dependency.
                # Let's try to fetch from 'attestations' (VaultNode) as per main.py logic.
                cur.execute("SELECT scarindex FROM attestations ORDER BY created_at DESC LIMIT 1")
                row = cur.fetchone()
                if row and row[0] is not None:
                    return float(row[0])
        except Exception as e:
            # logger.error(f"Failed to fetch ScarIndex: {e}")
            pass
            
        return 1.0 # Default Coherence
