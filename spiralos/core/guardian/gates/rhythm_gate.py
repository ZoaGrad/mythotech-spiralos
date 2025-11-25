"""Freshness gate for external telemetry leveraging ΔΩ.11 rhythm constants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional

from core.guardian.rhythm import RhythmBounds


EXTERNAL_WITNESS_BOUNDS = RhythmBounds(
    label="external_witness_events",
    max_staleness_seconds=15 * 60,  # 15 minutes to align with guardian cadence
)


@dataclass
class RhythmDecision:
    allowed: bool
    staleness_seconds: float
    reason: Optional[str] = None


class RhythmGate:
    def __init__(
        self,
        bounds: RhythmBounds = EXTERNAL_WITNESS_BOUNDS,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self.bounds = bounds
        self.now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def evaluate(self, timestamp: datetime) -> RhythmDecision:
        normalized = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
        staleness = max(0.0, (self.now_provider() - normalized).total_seconds())
        allowed = staleness <= self.bounds.max_staleness_seconds
        reason = None if allowed else "stale_event"
        return RhythmDecision(allowed=allowed, staleness_seconds=staleness, reason=reason)


__all__ = ["EXTERNAL_WITNESS_BOUNDS", "RhythmDecision", "RhythmGate"]
