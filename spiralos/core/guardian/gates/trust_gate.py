"""Trust gate for external witness telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Set

from ...external.schemas import ExternalWitnessEvent
from ...external.validators import build_allowlist, compute_trust_score


@dataclass
class TrustDecision:
    allowed: bool
    trust_score: float
    reason: Optional[str] = None


class TrustGate:
    """Deterministic trust scoring and gating for external signals."""

    def __init__(
        self,
        *,
        allowlist: Iterable[str] | None = None,
        trust_threshold: float = 0.6,
        expected_signatures: Mapping[str, str] | None = None,
        signature_validator=None,
    ) -> None:
        self.allowlist: Set[str] = build_allowlist(allowlist)
        self.trust_threshold = trust_threshold
        self.expected_signatures = dict(expected_signatures or {})
        self.signature_validator = signature_validator

    def evaluate(self, event: ExternalWitnessEvent) -> TrustDecision:
        score, reason = compute_trust_score(
            event,
            allowlist=self.allowlist,
            expected_signatures=self.expected_signatures,
            signature_validator=self.signature_validator,
        )

        allowed = score >= self.trust_threshold
        rejection_reason = reason if not allowed else None
        if not allowed and not rejection_reason:
            rejection_reason = "low_trust"

        return TrustDecision(allowed=allowed, trust_score=score, reason=rejection_reason)


__all__ = ["TrustDecision", "TrustGate"]
