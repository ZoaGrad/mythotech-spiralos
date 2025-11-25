"""Guardian anomaly detector for Supabase-backed coherence signals."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List, Sequence

from supabase import Client

PANIC_FLOOR = 0.30
OVERLOAD_CEILING = 0.90


@dataclass
class Anomaly:
    """Structured anomaly finding."""

    created_at: datetime
    value: float
    reason: str

    def __str__(self) -> str:  # pragma: no cover - presentation only
        timestamp = self.created_at.isoformat()
        return f"{timestamp} :: {self.reason} (value={self.value:.3f})"


class AnomalyDetector:
    """Detects coherence fractures using recent ScarIndex signals."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def _fetch_recent_signals(self) -> Sequence[dict[str, Any]]:
        response = (
            self.supabase.table("scarindex_calculations")
            .select("value,created_at")
            .order("created_at", desc=True)
            .limit(24)
            .execute()
        )
        return response.data or []

    def detect_anomalies(self) -> List[Anomaly]:
        """Return anomalies when signals breach constitutional thresholds."""
        rows = self._fetch_recent_signals()
        anomalies: List[Anomaly] = []

        for row in rows:
            value = row.get("value")
            created_raw = row.get("created_at")
            if value is None or created_raw is None:
                continue

            created_at = (
                created_raw if isinstance(created_raw, datetime) else datetime.fromisoformat(created_raw)
            )
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            if value < PANIC_FLOOR:
                anomalies.append(Anomaly(created_at=created_at, value=value, reason="Coherence below panic floor"))
            elif value > OVERLOAD_CEILING:
                anomalies.append(Anomaly(created_at=created_at, value=value, reason="Coherence above overload ceiling"))

        return anomalies
