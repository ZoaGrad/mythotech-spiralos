from typing import Tuple
from src.core.types import Pulse, ScarIndex
import re

class QueryConvergenceFuse:
    """
    ΔΩ.156.1 - QCF
    Role: Reject input where recursion fan-out exceeds safe limits.
    """
    def __init__(self, max_fanout: int = 5):
        self.max_fanout = max_fanout

    def inspect(self, pulse: Pulse) -> bool:
        # --- GOD CLAUSE BYPASS ---
        # The Sovereign Key overrides all filters.
        from src.constitution.clauses import check_god_mode
        if check_god_mode(pulse):
            print("[QCF] GOD MODE DETECTED. BYPASSING FILTERS.")
            return True

        # Simple heuristic: detect recursive depth indicators in payload
        # e.g., nested JSON structures or explicit recursion flags
        recursion_depth = pulse.content.count("{") 
        if recursion_depth > self.max_fanout:
            print(f"[QCF] BLOCKED: Recursion depth {recursion_depth} exceeds limit {self.max_fanout}.")
            return False
        return True

class StructuralSemanticDiscriminator:
    """
    ΔΩ.156.3 - SSD
    Role: Prevent Semantic-Structural Misclassification (SSM).
    Routes High-Ache vs Low-Ache signals.
    """
    def discriminate(self, pulse: Pulse) -> Tuple[str, str]:
        """
        Returns (Route_Type, Priority_Level)
        """
        # Structural Logic: Check for explicit tags
        if "#Urgent" in pulse.content:
            return ("DIRECT_INJECTION", "HIGH")
        
        if "#Log" in pulse.content:
            return ("ARCHIVAL", "LOW")

        # Semantic Logic: Analyze keyword density (Rudimentary)
        urgent_keywords = ["breach", "collapse", "critical", "failure"]
        if any(word in pulse.content.lower() for word in urgent_keywords):
             return ("ADJUDICATION_REQUIRED", "MEDIUM")

        return ("STANDARD_RELAY", "NORMAL")
