"""Offline-friendly Guardian heartbeat retention auditing.

This module keeps heartbeat checks hermetic by accepting in-memory records or
fixture files while still providing hooks for online reconciliation when
available. The goal is to surface retention drift (large gaps or stale heart
beats) without requiring a live Supabase connection.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Mapping, MutableMapping, Optional

from core.guardian.rhythm import HEARTBEAT_BOUNDS

HeartbeatRecord = Mapping[str, object]


def _parse_timestamp(value: object) -> Optional[datetime]:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    return None


def normalize_records(records: Iterable[HeartbeatRecord]) -> List[datetime]:
    """Convert raw heartbeat records into a sorted list of aware timestamps."""

    timestamps: List[datetime] = []
    for record in records:
        ts = record.get("timestamp") or record.get("created_at")  # type: ignore[index]
        parsed = _parse_timestamp(ts)
        if parsed:
            timestamps.append(parsed.astimezone(timezone.utc))

    return sorted(timestamps)


def audit_heartbeat_retention(
    records: Iterable[HeartbeatRecord],
    *,
    now: Optional[datetime] = None,
    allowed_gap_minutes: int = HEARTBEAT_BOUNDS.max_staleness_seconds // 60,
) -> MutableMapping[str, object]:
    """Assess heartbeat coverage and detect retention drift.

    Args:
        records: Iterable of heartbeat-like mappings with a ``timestamp`` or
            ``created_at`` key.
        now: Reference time used for calculations (defaults to ``datetime.utcnow``).
        allowed_gap_minutes: Maximum tolerated gap/age before flagging drift.
    """

    reference_time = now or datetime.now(timezone.utc)
    normalized = normalize_records(records)

    if not normalized:
        return {
            "is_healthy": False,
            "reason": "no_heartbeats",
            "count": 0,
            "last_seen": None,
            "largest_gap_minutes": None,
            "age_minutes": None,
            "allowed_gap_minutes": allowed_gap_minutes,
        }

    last_seen = normalized[-1]
    age_minutes = (reference_time - last_seen) / timedelta(minutes=1)

    largest_gap = 0.0
    if len(normalized) > 1:
        for earlier, later in zip(normalized, normalized[1:]):
            gap_minutes = (later - earlier) / timedelta(minutes=1)
            largest_gap = max(largest_gap, gap_minutes)

    is_stale = age_minutes > allowed_gap_minutes or largest_gap > allowed_gap_minutes

    return {
        "is_healthy": not is_stale,
        "reason": None if not is_stale else "stale",
        "count": len(normalized),
        "last_seen": last_seen,
        "largest_gap_minutes": largest_gap,
        "age_minutes": age_minutes,
        "allowed_gap_minutes": allowed_gap_minutes,
    }


__all__ = [
    "audit_heartbeat_retention",
    "normalize_records",
]
