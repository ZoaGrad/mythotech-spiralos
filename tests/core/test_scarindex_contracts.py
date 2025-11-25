import pytest
from datetime import datetime, timezone

from core.adapters import scarindex as scarindex_adapter

from core.contracts.scarindex import (
    GuardianScarIndexCurrent,
    GuardianScarIndexHistory,
    ScarIndexBreakdown,
    ScarIndexState,
)


def test_guardian_current_schema_validation():
    row = {
        "bridge_id": "bridge-alpha",
        "scar_value": 0.75,
        "metadata": {},
        "updated_at": datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        "created_at": datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
    }

    GuardianScarIndexCurrent.validate_row_shape(row)

    row_with_extra = {**row, "unexpected": True}
    with pytest.raises(ValueError):
        GuardianScarIndexCurrent.validate_row_shape(row_with_extra)

    row_missing = row.copy()
    row_missing.pop("scar_value")
    with pytest.raises(ValueError):
        GuardianScarIndexCurrent.validate_row_shape(row_missing)


def test_guardian_history_schema_validation():
    row = {
        "bridge_id": "bridge-alpha",
        "scar_value": 0.75,
        "delta": 0.05,
        "source": "telemetry_normalize",
        "metadata": {},
        "timestamp": datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        "created_at": datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
    }

    GuardianScarIndexHistory.validate_row_shape(row)

    row_with_extra = {**row, "unexpected": True}
    with pytest.raises(ValueError):
        GuardianScarIndexHistory.validate_row_shape(row_with_extra)


def test_scarindex_state_to_guardian_shapes():
    state = ScarIndexState(
        phase="ΔΩ.149.C",
        value=0.9,
        trend="up",
        recorded_at=datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        witness_id="spiralos-core",
        lineage_hash="hash",
        breakdown=[
            ScarIndexBreakdown(
                component="operational",
                ache_value=0.1,
                ache_delta=0.01,
                weight=0.35,
                rationale="test",
            )
        ],
        metadata={"source": "test"},
    )

    current = state.to_guardian_current("bridge-alpha").model_dump()
    history = state.to_guardian_history("bridge-alpha", previous_value=0.5).model_dump()

    GuardianScarIndexCurrent.validate_row_shape(current)
    GuardianScarIndexHistory.validate_row_shape(history)


def test_adapter_normalizes_timestamps(monkeypatch):
    """ScarIndex adapter must honor locked UTC timestamp semantics."""

    monkeypatch.setattr(
        scarindex_adapter,
        "get_spiralos_status",
        lambda: {
            "timestamp": "2025-01-01T12:00:00Z",
            "coherence": {
                "current_scarindex": 0.8,
                "target_scarindex": 0.75,
                "error": 0.05,
            },
        },
    )

    current, history = scarindex_adapter.to_guardian_scarindex_records(
        "bridge-alpha", previous_value=0.7, source="telemetry_normalize"
    )

    assert current.updated_at.tzinfo is not None
    assert history.timestamp.tzinfo is not None

    GuardianScarIndexCurrent.validate_row_shape(current.model_dump())
    GuardianScarIndexHistory.validate_row_shape(history.model_dump())
