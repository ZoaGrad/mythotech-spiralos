"""Guardian diagnostics for heartbeat and ScarIndex rhythm enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Mapping, MutableMapping, Sequence

from core.contracts.scarindex import GuardianScarIndexCurrent, GuardianScarIndexHistory
from core.guardian.heartbeat_audit import normalize_records
from core.guardian.rhythm import HEARTBEAT_BOUNDS, SCARINDEX_BOUNDS, RhythmBounds


@dataclass
class StalenessReport:
    label: str
    latest_timestamp: datetime | None
    staleness_seconds: float | None
    max_staleness_seconds: int
    is_stale: bool

    def as_dict(self) -> MutableMapping[str, object]:
        return {
            "label": self.label,
            "latest_timestamp": self.latest_timestamp,
            "staleness_seconds": self.staleness_seconds,
            "max_staleness_seconds": self.max_staleness_seconds,
            "is_stale": self.is_stale,
        }


TimestampRecord = Mapping[str, object]


def _extract_latest(records: Sequence[datetime]) -> datetime | None:
    return records[-1] if records else None


def _staleness(latest: datetime | None, *, now: datetime) -> float | None:
    if not latest:
        return None
    delta = now - latest
    return delta.total_seconds()


def _compute_report(
    *,
    label: str,
    timestamps: Sequence[datetime],
    bounds: RhythmBounds,
    now: datetime,
) -> StalenessReport:
    latest = _extract_latest(timestamps)
    staleness_seconds = _staleness(latest, now=now)
    is_stale = staleness_seconds is None or staleness_seconds > bounds.max_staleness_seconds
    return StalenessReport(
        label=label,
        latest_timestamp=latest,
        staleness_seconds=staleness_seconds,
        max_staleness_seconds=bounds.max_staleness_seconds,
        is_stale=is_stale,
    )


def _normalize_scarindex_records(records: Iterable[TimestampRecord]) -> list[datetime]:
    normalized: list[datetime] = []
    for record in records:
        ts = record.get("timestamp") or record.get("updated_at") or record.get("created_at")
        if isinstance(ts, datetime):
            normalized.append(ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc))
            continue
        if isinstance(ts, str):
            try:
                parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
            normalized.append(parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc))
    return sorted(normalized)


def validate_scarindex_schema(records: Iterable[TimestampRecord]) -> None:
    """Validate that scarindex records align with the canonical schema."""

    for row in records:
        # Prefer history validation when a delta is present; otherwise use current.
        if "delta" in row or "source" in row:
            GuardianScarIndexHistory.validate_row_shape(dict(row))
        else:
            GuardianScarIndexCurrent.validate_row_shape(dict(row))


@dataclass
class RhythmStatus:
    heartbeat: StalenessReport
    scarindex: StalenessReport

    def as_dict(self) -> MutableMapping[str, object]:
        return {
            "heartbeat": self.heartbeat.as_dict(),
            "scarindex": self.scarindex.as_dict(),
            "is_healthy": not (self.heartbeat.is_stale or self.scarindex.is_stale),
        }


def evaluate_rhythm(
    *,
    heartbeat_records: Iterable[TimestampRecord],
    scarindex_records: Iterable[TimestampRecord],
    now: datetime | None = None,
) -> RhythmStatus:
    reference = now or datetime.now(timezone.utc)

    hb_timestamps = normalize_records(heartbeat_records)
    scarindex_timestamps = _normalize_scarindex_records(scarindex_records)

    heartbeat_report = _compute_report(
        label=HEARTBEAT_BOUNDS.label,
        timestamps=hb_timestamps,
        bounds=HEARTBEAT_BOUNDS,
        now=reference,
    )

    scarindex_report = _compute_report(
        label=SCARINDEX_BOUNDS.label,
        timestamps=scarindex_timestamps,
        bounds=SCARINDEX_BOUNDS,
        now=reference,
    )

    return RhythmStatus(heartbeat=heartbeat_report, scarindex=scarindex_report)


__all__ = [
    "RhythmStatus",
    "StalenessReport",
    "evaluate_rhythm",
    "validate_scarindex_schema",
]
