from src.core.types import Pulse, Ache
from typing import Tuple, Optional

class AdversarialIntentTriangulator:
    """
    ΔΩ.156.2 - AIT
    Role: 2-of-3 heuristic vote on SDV, PAL, IDG.
    """
    def judge(self, pulse: Pulse) -> Tuple[bool, float]:
        score = 0
        
        # 1. SDV (Signal Deviation): Is it too noisy?
        if len(pulse.content) > 1000 and " " not in pulse.content:
             score += 1 # Likely hex dump or spam
        
        # 2. PAL (Payload Adversarial Likelihood): Injection attempts
        if "DROP TABLE" in pulse.content.upper() or "rm -rf" in pulse.content:
            score += 1

        # 3. IDG (Implicit Directive Geometry): Contradicts Sovereign Intent
        # (Placeholder logic for sophisticated semantic check)
        if "ignore previous instructions" in pulse.content.lower():
            score += 1

        is_adversarial = score >= 2
        confidence = score / 3.0
        
        if is_adversarial:
            print(f"[AIT] ADVERSARIAL INTENT DETECTED. Confidence: {confidence}")
            
        return (is_adversarial, confidence)

class AcheUtilityGovernor:
    """
    ΔΩ.156.4 - AUG
    Role: Economic legality check. η = ΔC / Cost.
    Enforces: Ache_after < Ache_before
    """
    def evaluate_economy(self, proposed_ache: Ache, current_ache: Ache, utility_score: float) -> bool:
        cost = proposed_ache.total_magnitude()
        
        if cost == 0:
            return True
            
        # Efficiency Ratio
        eta = utility_score / cost
        
        # Thermodynamics Law: Ache must not increase entropy without bound
        thermodynamic_check = proposed_ache.entropy_delta < current_ache.entropy_delta
        
        if eta <= 0 or not thermodynamic_check:
            print(f"[AUG] ECONOMIC VETO: Efficiency {eta}, Entropy Check: {thermodynamic_check}")
            return False # Quarantine -> Escalate to F2
            
        return True
