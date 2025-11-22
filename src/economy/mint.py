from typing import Dict

MINT_DIFFICULTY = 10.0

def calculate_mint_amount(ache_before: float, ache_after: float, scar_index: float) -> float:
    """
    Minting Formula:
    Value = (Thermodynamic Work) * (Structural Integrity) * Multiplier
    
    Args:
        ache_before: Entropy state before the pulse (History).
        ache_after: Entropy state after the pulse (Current).
        scar_index: System coherence score (0.0 - 1.0).
        
    Returns:
        float: Amount of ScarCoin (SCAR) minted.
    """
    # 1. Thermodynamic Work (Delta C)
    delta_c = ache_before - ache_after
    
    # Constraint: No minting if entropy increased (Delta C <= 0)
    if delta_c <= 0:
        return 0.0
        
    # Constraint: No minting if system is unstable (ScarIndex < 0.7)
    if scar_index < 0.7:
        return 0.0
        
    # 2. The Formula
    mint_amount = delta_c * scar_index * MINT_DIFFICULTY
    
    return round(mint_amount, 4)
