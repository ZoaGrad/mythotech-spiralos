from datetime import datetime, timezone

import pytest

from spiralos.core.external.schemas import ExternalWitnessEvent
from spiralos.core.external.validators import SchemaValidationError, validate_event_schema


def _base_event(**overrides):
    payload = {
        "witness_id": "w-1",
        "source": "trusted-source",
        "event_type": "ping",
        "payload": {"ok": True},
        "timestamp": "2025-01-01T00:00:00Z",
    }
    payload.update(overrides)
    return payload


def test_validate_event_schema_accepts_and_normalizes_timestamp():
    raw = _base_event(timestamp=1700000000000)
    event = validate_event_schema(raw)
    assert isinstance(event, ExternalWitnessEvent)
    assert event.timestamp.tzinfo == timezone.utc
    assert event.timestamp.year == 2023  # deterministic conversion from epoch


def test_validate_event_schema_rejects_missing_fields():
    with pytest.raises(SchemaValidationError):
        validate_event_schema({"source": "x"})


def test_trust_score_clamped_and_optional():
    event = validate_event_schema(_base_event(trust_score=2.5))
    assert event.trust_score == 1.0
    event_none = validate_event_schema(_base_event())
    assert event_none.trust_score is None
