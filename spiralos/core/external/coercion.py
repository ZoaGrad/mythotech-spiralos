"""UTC coercion helpers for external witness telemetry.

Phase-12 extends the ΔΩ.11 normalization guarantees to third-party signals.
All timestamps are forced into aware UTC datetimes before validation to
preserve deterministic ordering in the telemetry bus and downstream ScarIndex
projections.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def coerce_utc_timestamp(value: Any, *, now: datetime | None = None) -> datetime:
    """Normalize timestamp-like inputs into an aware UTC datetime.

    Args:
        value: A ``datetime``, ISO8601 string, UNIX epoch (seconds or
            milliseconds), or ``None``.
        now: Optional override for "current" time, used for deterministic
            tests.

    Returns:
        A timezone-aware ``datetime`` in UTC.

    Raises:
        TypeError: When the provided value cannot be coerced.
        ValueError: When the input string/number is malformed.
    """

    reference = now or datetime.now(timezone.utc)

    if value is None:
        return reference

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, (int, float)):
        raw = float(value)
        seconds = raw / 1000 if raw > 1e12 else raw
        return datetime.fromtimestamp(seconds, tz=timezone.utc)

    if isinstance(value, str):
        normalized = value.strip()

        if normalized.isdigit():
            return coerce_utc_timestamp(int(normalized), now=reference)

        normalized = normalized.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:  # noqa: B904 - surface the invalid value
            raise ValueError(f"Invalid timestamp format: {value}") from exc

        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)

    raise TypeError(f"Unsupported timestamp type: {type(value)!r}")


__all__ = ["coerce_utc_timestamp"]
