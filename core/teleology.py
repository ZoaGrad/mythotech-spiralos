from dataclasses import dataclass
from typing import Dict

@dataclass
class TauVector:
    """
    Represents a Teleological Vector (Tau) used for alignment checks.
    """
    components: Dict[str, float]

    def dot(self, other: Dict[str, float]) -> float:
        """
        Compute dot product (alignment score) with another vector (e.g., action features).
        """
        score = 0.0
        for key, value in other.items():
            if key in self.components:
                score += self.components[key] * value
        return score
