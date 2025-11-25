from datetime import datetime, timedelta, timezone

from spiralos.core.external.adapter import ExternalWitnessAdapter


def test_adapter_accepts_allowlisted_event_with_trust_score():
    fixed_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    adapter = ExternalWitnessAdapter(allowlist=["trusted-source"], now_provider=lambda: fixed_now)

    result = adapter.ingest(
        {
            "witness_id": "witness-1",
            "source": "trusted-source",
            "event_type": "sync",
            "payload": {"ok": True},
            "timestamp": fixed_now.isoformat(),
            "signature": "sig",
        }
    )

    assert result.accepted is True
    assert adapter.accepted[-1]["trust_score"] == 1.0
    assert adapter.accepted[-1]["ingested_at"] == fixed_now


def test_adapter_quarantines_schema_failures_deterministically():
    fixed_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    adapter = ExternalWitnessAdapter(now_provider=lambda: fixed_now)

    result = adapter.ingest({"source": "missing-fields"})

    assert result.accepted is False
    assert result.reason == "schema_failure"
    assert adapter.quarantine[-1].reason == "schema_failure"


def test_adapter_blocks_stale_events_via_rhythm_gate():
    reference = datetime(2025, 1, 1, tzinfo=timezone.utc)
    stale_ts = reference - timedelta(minutes=20)
    adapter = ExternalWitnessAdapter(allowlist=["trusted-source"], now_provider=lambda: reference)

    result = adapter.ingest(
        {
            "witness_id": "witness-2",
            "source": "trusted-source",
            "event_type": "sync",
            "payload": {},
            "timestamp": stale_ts.isoformat(),
        }
    )

    assert result.accepted is False
    assert adapter.quarantine[-1].reason == "stale_event"
