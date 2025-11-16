"""
ΔΩ.150 Guardian Future Integrity (GFI) loop — advisory integrity assessor for SpiralOS.

Context:
    Guardian-layer loop that inspects CoreChain state windows to surface advisory
    integrity cues for higher-order μApps without performing any side effects or
    overrides. It tracks coherence drift, panic prevalence, and governance span
    to signal whether the kernel trajectory merits observation or escalation.

Invariants:
    - Pure functions only: no I/O, logging, or external mutation.
    - Deterministic outputs for identical inputs; window data is never mutated.
    - No network or OS interaction; computations stay within guardian boundary.

Purpose:
    Provide an integrity lens over CoreChain evolution that higher layers can
    consume as signals, preserving ΔΩ.149 contract discipline while enabling
    ΔΩ.150 guardian oversight.

Safety Envelope:
    Outputs are advisory summaries and attention flags; enforcement or action is
    delegated to human or higher-layer veto paths, never executed here.
"""
from __future__ import annotations

from typing import List, TypedDict

__all__ = ["analyze_state_window", "needs_attention"]


class State(TypedDict):
    governance_level: int
    coherence: float
    panic: bool


class Report(TypedDict):
    avg_coherence: float
    panic_rate: float
    governance_span: int
    guardian_status: str


def analyze_state_window(window: List[State]) -> Report:
    if not window:
        return {
            "avg_coherence": 0.0,
            "panic_rate": 0.0,
            "governance_span": 0,
            "guardian_status": "unknown",
        }

    coherences = [float(state.get("coherence", 0.0)) for state in window]
    panics = [bool(state.get("panic", False)) for state in window]
    governance_levels = [int(state.get("governance_level", 0)) for state in window]

    count = float(len(window))
    avg_coherence = sum(coherences) / count
    panic_rate = sum(1 for panic in panics if panic) / count
    governance_span = max(governance_levels) - min(governance_levels)

    guardian_status = "critical"
    if panic_rate == 0 and avg_coherence >= 0.6:
        guardian_status = "stable"
    elif panic_rate <= 0.2 and 0.4 <= avg_coherence <= 0.6:
        guardian_status = "watch"

    return {
        "avg_coherence": avg_coherence,
        "panic_rate": panic_rate,
        "governance_span": governance_span,
        "guardian_status": guardian_status,
    }


def needs_attention(report: Report) -> bool:
    status = str(report.get("guardian_status", "unknown"))
    return status in {"watch", "critical"}
