"""Read-only SystemPulse adapter sourced from SpiralOS status snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.adapters import get_spiralos_status
from core.contracts.system import SystemPulse


def _parse_timestamp(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(timezone.utc)


def to_system_pulse() -> SystemPulse:
    """Translate SpiralOS.get_system_status() output into a SystemPulse contract."""

    status = get_spiralos_status()
    coherence = status.get("coherence", {})
    panic_info = status.get("panic_frames", {})

    scarindex_value = float(coherence.get("current_scarindex") or 0.0)
    panic_state = "active" if panic_info.get("active_count") else "clear"
    mode = "panic-monitor" if panic_state == "active" else "operational"
    health_score = max(0.0, min(1.0, scarindex_value))
    timestamp = _parse_timestamp(status.get("timestamp"))

    notes = (
        "PID error={error} | active_panic_frames={frames}".format(
            error=coherence.get("error"), frames=panic_info.get("active_count", 0)
        )
    )

    return SystemPulse(
        captured_at=timestamp,
        mode=mode,
        scarindex_value=scarindex_value,
        panic_state=panic_state,
        governance_phase="ΔΩ.149.C",
        health_score=health_score,
        notes=notes,
    )
