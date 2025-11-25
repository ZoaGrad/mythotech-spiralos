"""Read-only adapter that projects SpiralOS coherence telemetry into ΔΩ contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.adapters import get_spiralos_status
from core.contracts.scarindex import (
    GuardianScarIndexCurrent,
    GuardianScarIndexHistory,
    ScarIndexBreakdown,
    ScarIndexState,
)
from core.scarindex import ScarIndexOracle


def _parse_timestamp(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(timezone.utc)


def to_scar_index_state() -> ScarIndexState:
    """Map the latest SpiralOS status snapshot into a ScarIndexState contract."""

    status = get_spiralos_status()
    coherence = status.get("coherence", {})
    timestamp = _parse_timestamp(status.get("timestamp"))

    current_value = float(coherence.get("current_scarindex") or 0.0)
    target_value = float(coherence.get("target_scarindex") or 0.0)
    error = float(coherence.get("error") or 0.0)

    if current_value > target_value + 0.01:
        trend = "up"
    elif current_value < target_value - 0.01:
        trend = "down"
    else:
        trend = "stable"

    breakdown = [
        ScarIndexBreakdown(
            component=component,
            ache_value=max(current_value * weight, 0.0),
            ache_delta=-error * weight,
            weight=weight,
            rationale=f"PID error vs. target {target_value:.2f}",
        )
        for component, weight in ScarIndexOracle.WEIGHTS.items()
    ]

    return ScarIndexState(
        phase="ΔΩ.149.C",
        value=current_value,
        trend=trend,
        recorded_at=timestamp,
        witness_id="spiralos-core",
        lineage_hash=status.get("timestamp", "ΔΩ.149"),
        breakdown=breakdown,
        metadata={
            "source": "SpiralOS.get_system_status()",
            "target": target_value,
            "pid_error": error,
        },
    )


def to_guardian_scarindex_records(
    bridge_id: str,
    *,
    previous_value: float | None = None,
    source: str = "telemetry_normalize",
) -> tuple[GuardianScarIndexCurrent, GuardianScarIndexHistory]:
    """Project the ScarIndex contract into guardian schema-aligned rows.

    The function returns both the current-row projection (idempotent update) and
    a history-row payload suitable for insertion. This keeps the adapter as the
    single source of truth for schema alignment between Python contracts and the
    Supabase migrations defined in ``spiral_supabase/migrations``.
    """

    state = to_scar_index_state()
    return (
        state.to_guardian_current(bridge_id),
        state.to_guardian_history(
            bridge_id,
            previous_value=previous_value,
            source=source,
        ),
    )
