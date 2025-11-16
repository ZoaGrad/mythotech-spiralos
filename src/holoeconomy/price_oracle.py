"""
ΔΩ.150 HoloEconomy Price Oracle — binds coherence and governance into deterministic pricing.

Context:
    Positioned at the holoeconomy engine boundary, the price oracle converts
    CoreChain state primitives into a single scalar price that upstream
    ScarCoin minting and liquidity policy modules can reference. It adheres to
    ΔΩ.149 contract discipline: pure, side-effect-free, and deterministic
    across identical inputs.

Invariants:
    - Pure computation only; no I/O, logging, or network access.
    - Inputs are never mutated; state is read-only and re-expressed as floats
      and ints for stability.
    - Pricing is clamped to [0.1, 3.0] to maintain holoeconomic safety bounds.

Purpose:
    Provide a canonical price signal derived from coherence, governance level,
    and panic indicators so that holoeconomy decisions remain aligned with
    kernel stability and guardian oversight.

Safety Envelope:
    Outputs are advisory metrics consumed by ScarCoin mint modules and related
    holoeconomy components; this oracle never effects state changes directly.
"""
from __future__ import annotations

from typing import TypedDict

__all__ = ["compute_price", "classify_price_level"]


class State(TypedDict):
    governance_level: int
    coherence: float
    panic: bool


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def compute_price(state: State) -> float:
    governance_level = int(state["governance_level"])
    coherence = float(state["coherence"])
    panic = bool(state["panic"])

    base_price = 1.0
    governance_factor = 0.05 * governance_level
    panic_penalty = 0.4 if panic else 0.0

    price = base_price + coherence + governance_factor - panic_penalty
    return _clamp(price, 0.1, 3.0)


def classify_price_level(price: float) -> str:
    if price >= 2.0:
        return "high"
    if price >= 1.0:
        return "medium"
    return "low"
