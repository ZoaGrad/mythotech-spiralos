"""Gated adapter for ingesting external witness telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, Mapping

from .schemas import ExternalQuarantineRecord, ExternalWitnessEvent
from .validators import SchemaValidationError, quarantine_record, validate_event_schema
from ..guardian.gates.rhythm_gate import RhythmGate
from ..guardian.gates.trust_gate import TrustGate


@dataclass
class AdapterResult:
    accepted: bool
    record: Mapping[str, Any]
    reason: Optional[str] = None


class ExternalWitnessAdapter:
    """Adapter that enforces trust and rhythm gates before persistence."""

    def __init__(
        self,
        *,
        allowlist: Iterable[str] | None = None,
        trust_threshold: float = 0.6,
        expected_signatures: Mapping[str, str] | None = None,
        now_provider: Callable[[], datetime] | None = None,
        rhythm_gate: RhythmGate | None = None,
        trust_gate: TrustGate | None = None,
    ) -> None:
        self.now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        self.trust_gate = trust_gate or TrustGate(
            allowlist=allowlist,
            trust_threshold=trust_threshold,
            expected_signatures=expected_signatures,
        )
        self.rhythm_gate = rhythm_gate or RhythmGate(now_provider=self.now_provider)
        self.accepted: list[dict[str, Any]] = []
        self.quarantine: list[ExternalQuarantineRecord] = []

    def ingest(self, raw_event: Mapping[str, Any]) -> AdapterResult:
        try:
            event = validate_event_schema(raw_event)
        except SchemaValidationError as exc:
            record = quarantine_record("schema_failure", raw_event, str(exc))
            self._quarantine(record)
            return AdapterResult(False, record.model_dump(), "schema_failure")

        trust_decision = self.trust_gate.evaluate(event)
        if not trust_decision.allowed:
            record = quarantine_record(trust_decision.reason or "low_trust", raw_event)
            self._quarantine(record)
            return AdapterResult(False, record.model_dump(), trust_decision.reason or "low_trust")

        rhythm_decision = self.rhythm_gate.evaluate(event.timestamp)
        if not rhythm_decision.allowed:
            record = quarantine_record(rhythm_decision.reason or "stale_event", raw_event)
            self._quarantine(record)
            return AdapterResult(False, record.model_dump(), rhythm_decision.reason or "stale_event")

        stored = self._persist(event, trust_decision.trust_score)
        return AdapterResult(True, stored, None)

    def _persist(self, event: ExternalWitnessEvent, trust_score: float) -> Dict[str, Any]:
        record = {
            "witness_id": event.witness_id,
            "source": event.source,
            "event_type": event.event_type,
            "payload": event.payload,
            "signature": event.signature,
            "metadata": event.metadata,
            "trust_score": trust_score,
            "timestamp": event.timestamp.astimezone(timezone.utc),
            "ingested_at": self.now_provider(),
        }
        self.accepted.append(record)
        return record

    def _quarantine(self, record: ExternalQuarantineRecord) -> None:
        self.quarantine.append(record)


__all__ = ["AdapterResult", "ExternalWitnessAdapter"]
