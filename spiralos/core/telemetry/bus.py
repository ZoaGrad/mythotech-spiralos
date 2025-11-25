"""Unified telemetry bus that merges internal, external, and heartbeat flows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, MutableMapping

from ..external.coercion import coerce_utc_timestamp
from .router import TelemetryRouter


@dataclass
class TelemetryEnvelope:
    kind: str
    source: str
    event_type: str
    payload: Mapping[str, Any]
    timestamp: datetime
    metadata: MutableMapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "source": self.source,
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }


class TelemetryBus:
    def __init__(self, router: TelemetryRouter | None = None) -> None:
        self.router = router or TelemetryRouter()

    def publish(
        self,
        *,
        kind: str,
        source: str,
        event_type: str,
        payload: Mapping[str, Any],
        timestamp: Any | None = None,
        metadata: MutableMapping[str, Any] | None = None,
    ) -> object:
        envelope = TelemetryEnvelope(
            kind=kind,
            source=source,
            event_type=event_type,
            payload=payload,
            timestamp=coerce_utc_timestamp(timestamp),
            metadata=metadata or {},
        )

        return self.router.route(kind, envelope.as_dict())


__all__ = ["TelemetryBus", "TelemetryEnvelope"]
