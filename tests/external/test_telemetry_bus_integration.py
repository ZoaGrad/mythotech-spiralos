from datetime import datetime, timezone

from spiralos.core.external.adapter import ExternalWitnessAdapter
from spiralos.core.telemetry.bus import TelemetryBus
from spiralos.core.telemetry.router import TelemetryRouter


def test_bus_routes_external_internal_and_heartbeat():
    fixed_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    adapter = ExternalWitnessAdapter(allowlist=["bus-source"], now_provider=lambda: fixed_now)

    internal_events: list[dict] = []
    heartbeat_events: list[datetime] = []

    router = TelemetryRouter()

    def _external_handler(envelope: dict):
        payload = {
            "witness_id": envelope["metadata"].get("witness_id", "external"),
            "source": envelope["source"],
            "event_type": envelope["event_type"],
            "payload": envelope["payload"],
            "timestamp": envelope["timestamp"],
            "signature": envelope["metadata"].get("signature"),
        }
        return adapter.ingest(payload)

    router.register("external", _external_handler)
    router.register("internal", lambda envelope: internal_events.append(envelope))
    router.register("heartbeat", lambda envelope: heartbeat_events.append(envelope["timestamp"]))

    bus = TelemetryBus(router)

    bus.publish(
        kind="external",
        source="bus-source",
        event_type="sync",
        payload={"count": 1},
        timestamp=fixed_now,
        metadata={"witness_id": "witness-bus"},
    )

    bus.publish(
        kind="internal",
        source="core",
        event_type="health",
        payload={"ok": True},
        timestamp=fixed_now,
        metadata={},
    )

    bus.publish(
        kind="heartbeat",
        source="guardian",
        event_type="heartbeat",
        payload={},
        timestamp=fixed_now,
        metadata={},
    )

    assert adapter.accepted
    assert internal_events[0]["event_type"] == "health"
    assert heartbeat_events[0] == fixed_now


def test_bus_handles_quarantine_reason_deterministically():
    fixed_now = datetime(2025, 1, 1, tzinfo=timezone.utc)
    adapter = ExternalWitnessAdapter(now_provider=lambda: fixed_now)
    router = TelemetryRouter()

    router.register("external", lambda envelope: adapter.ingest({"source": envelope["source"]}))
    bus = TelemetryBus(router)

    result = bus.publish(
        kind="external",
        source="missing-witness",
        event_type="sync",
        payload={},
        timestamp=fixed_now,
        metadata={},
    )

    assert result.accepted is False
    assert result.reason == "schema_failure"
