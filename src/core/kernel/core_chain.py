"""
ΔΩ.150 CoreChain — deterministic governance state machine for SpiralOS core-kernel.

Context:
    The core-chain governs governance_level, coherence, and panic flags as the
    minimal canonical state carried between μApps within the ΔΩ.149 contract
    lineage. It is pure, side-effect-free, and serialization-agnostic.

Invariants:
    - Inputs are never mutated; every transition returns a new state mapping.
    - No I/O, no network, no randomness; all operations are deterministic.
    - State coherence is clamped to [0.0, 1.0] to preserve contract safety.
    - Governance level adjustments are bounded to prevent drift beyond [0, 10].

Purpose:
    Provide the reference transition functions for applying signals, assessing
    safety, projecting the next state, and validating that transitions honor
    SpiralOS governance constraints under ΔΩ.149/ΔΩ.150 continuity.

Safety Envelope:
    Each function enforces panic propagation, coherence thresholds, and
    bounded governance adjustments so that core-kernel evolution remains
    auditable and resistant to unsafe or discontinuous jumps.
"""
from __future__ import annotations

from typing import Dict

__all__ = [
    "apply_signal",
    "is_safe",
    "next_state",
    "validate_transition",
]


State = Dict[str, object]


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _copy_state(state: State) -> State:
    return {
        "governance_level": int(state["governance_level"]),
        "coherence": float(state["coherence"]),
        "panic": bool(state["panic"]),
    }


def apply_signal(state: State, signal: State) -> State:
    base_state = _copy_state(state)
    signal_coherence = float(signal.get("coherence", base_state["coherence"]))
    weighted = 0.7 * base_state["coherence"] + 0.3 * signal_coherence
    new_coherence = _clamp(weighted, 0.0, 1.0)

    panic_from_signal = bool(signal.get("panic", False))
    panic_from_coherence = signal_coherence < 0.3
    panic = base_state["panic"] or panic_from_signal or panic_from_coherence

    return {
        "governance_level": base_state["governance_level"],
        "coherence": new_coherence,
        "panic": panic,
    }


def is_safe(state: State) -> bool:
    current = _copy_state(state)
    if current["panic"]:
        return False
    return current["coherence"] >= 0.25


def next_state(state: State) -> State:
    current = _copy_state(state)
    safe = is_safe(current)

    if safe:
        governance_level = min(10, current["governance_level"] + 1)
    else:
        governance_level = max(0, current["governance_level"] - 1)

    panic = current["panic"]
    if current["coherence"] >= 0.5:
        panic = False

    return {
        "governance_level": governance_level,
        "coherence": current["coherence"],
        "panic": panic,
    }


def validate_transition(old: State, new: State) -> bool:
    old_state = _copy_state(old)
    new_state = _copy_state(new)

    coherence_valid = 0.0 <= new_state["coherence"] <= 1.0
    governance_delta = new_state["governance_level"] - old_state["governance_level"]
    governance_valid = governance_delta in {-1, 0, 1}

    panic_valid = True
    if old_state["panic"] and not new_state["panic"]:
        panic_valid = old_state["coherence"] >= 0.5

    return coherence_valid and governance_valid and panic_valid
