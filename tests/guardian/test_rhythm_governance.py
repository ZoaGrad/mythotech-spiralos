from datetime import datetime, timezone

import pytest

from core.guardian.diagnostics import evaluate_rhythm, validate_scarindex_schema


def test_evaluate_rhythm_healthy():
    now = datetime(2025, 1, 1, 12, tzinfo=timezone.utc)
    heartbeat_records = [{"timestamp": "2025-01-01T11:55:00Z"}]
    scarindex_records = [
        {
            "timestamp": "2025-01-01T11:50:00Z",
            "scar_value": 0.81,
            "delta": 0.02,
            "metadata": {},
            "created_at": "2025-01-01T11:50:05Z",
        }
    ]

    status = evaluate_rhythm(
        heartbeat_records=heartbeat_records,
        scarindex_records=scarindex_records,
        now=now,
    )

    assert status.heartbeat.is_stale is False
    assert status.scarindex.is_stale is False


def test_evaluate_rhythm_detects_scarindex_staleness():
    now = datetime(2025, 1, 1, 12, tzinfo=timezone.utc)
    heartbeat_records = [{"timestamp": "2025-01-01T11:55:00Z"}]
    scarindex_records = [
        {
            "timestamp": "2024-12-31T00:00:00Z",
            "scar_value": 0.81,
            "delta": 0.02,
            "metadata": {},
            "created_at": "2024-12-31T00:00:00Z",
        }
    ]

    status = evaluate_rhythm(
        heartbeat_records=heartbeat_records,
        scarindex_records=scarindex_records,
        now=now,
    )

    assert status.scarindex.is_stale is True


def test_validate_scarindex_schema_drift_flagged():
    with pytest.raises(ValueError):
        validate_scarindex_schema(
            [
                {
                    "bridge_id": "bridge-alpha",
                    "scar_value": 0.8,
                    "delta": 0.1,
                    "timestamp": "2025-01-01T11:00:00Z",
                    "created_at": "2025-01-01T11:00:00Z",
                    "extra": True,
                }
            ]
        )
