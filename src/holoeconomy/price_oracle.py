"""
ΔΩ.150 context: price oracle as coherence-binding economic layer.
Deterministic, side-effect-free logic that binds coherence, panic, and governance
into a single scalar price signal. Serves as upstream input for ScarCoin mint module.
"""
from typing import TypedDict

__all__ = ["compute_price", "classify_price_level"]


class State(TypedDict):
    governance_level: int
    coherence: float
    panic: bool


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp ``value`` to the inclusive ``[minimum, maximum]`` range."""

    return max(minimum, min(maximum, value))


def compute_price(state: State) -> float:
    """Compute the deterministic price signal from CoreChain state."""
    coherence_factor = float(state["coherence"])
    governance_level = int(state["governance_level"])
    panic = bool(state["panic"])

    base_price = 1.0
    governance_factor = 0.05 * governance_level
    panic_penalty = 0.4 if panic else 0.0

    price = base_price + coherence_factor + governance_factor - panic_penalty
    return _clamp(price, 0.1, 3.0)


def classify_price_level(price: float) -> str:
    """Classify the price level into low, medium, or high."""
    if price >= 2.0:
        return "high"
    if price >= 1.0:
        return "medium"
    return "low"
