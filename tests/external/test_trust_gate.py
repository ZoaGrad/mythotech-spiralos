from datetime import datetime, timezone

from spiralos.core.external.schemas import ExternalWitnessEvent
from spiralos.core.guardian.gates.trust_gate import TrustGate


def _event(signature: str | None = None) -> ExternalWitnessEvent:
    return ExternalWitnessEvent(
        witness_id="witness-1",
        source="trusted",
        event_type="sync",
        payload={},
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        signature=signature,
    )


def test_trust_gate_allowlist():
    gate = TrustGate(allowlist=["trusted"], trust_threshold=0.7)
    decision = gate.evaluate(_event())
    assert decision.allowed is True
    assert decision.trust_score == 1.0


def test_trust_gate_signature_required():
    gate = TrustGate(expected_signatures={"witness-1": "sig"}, trust_threshold=0.8)
    decision_bad = gate.evaluate(_event(signature="bad"))
    assert decision_bad.allowed is False
    assert decision_bad.reason == "invalid_signature"

    decision_good = gate.evaluate(_event(signature="sig"))
    assert decision_good.allowed is True
    assert decision_good.trust_score >= 0.9
