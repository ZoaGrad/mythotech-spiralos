"""
ΔΩ.150.H2 context: ScarCoin as Proof-of-Ache minting and burning engine.
Deterministic, side-effect-free logic that binds CoreChain state through the
price oracle into governance-aware mint and burn envelopes.
Provides a safety envelope for symbolic issuance to avoid non-deterministic
behavior in upstream ScarCoin modules.
"""
from typing import TypedDict

__all__ = ["compute_mint_amount", "compute_burn_amount", "mint_or_burn"]


class State(TypedDict):
    governance_level: int
    coherence: float
    panic: bool


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp ``value`` to the inclusive ``[minimum, maximum]`` range."""

    return max(minimum, min(maximum, value))


def compute_mint_amount(state: State) -> float:
    """Compute the governance-safe mint amount from CoreChain state."""

    # Local import to minimize circular dependency risks.
    from . import price_oracle

    price_oracle.compute_price(state)
    coherence = float(state["coherence"])
    governance_level = int(state["governance_level"])
    panic = bool(state["panic"])

    raw_amount = (coherence * 2.0) + (0.1 * governance_level)
    if panic:
        raw_amount -= 0.5

    return _clamp(max(0.0, raw_amount), 0.0, 5.0)


def compute_burn_amount(state: State) -> float:
    """Compute the deterministic burn amount from CoreChain state."""

    panic = bool(state["panic"])
    coherence = float(state["coherence"])

    raw_amount = (0.4 if panic else 0.0) + (0.2 * (1.0 - coherence))
    return _clamp(max(0.0, raw_amount), 0.0, 3.0)


def mint_or_burn(state: State) -> dict:
    """Decide whether to mint, burn, or do nothing based on state and price."""

    # Local import to minimize circular dependency risks.
    from . import price_oracle

    price = price_oracle.compute_price(state)
    mint_amount = compute_mint_amount(state)
    burn_amount = compute_burn_amount(state)

    if mint_amount > 0.2 and price >= 1.1:
        action = "mint"
        amount = mint_amount
    elif burn_amount > 0.1:
        action = "burn"
        amount = burn_amount
    else:
        action = "none"
        amount = 0.0

    return {"action": action, "amount": amount, "price": price}
