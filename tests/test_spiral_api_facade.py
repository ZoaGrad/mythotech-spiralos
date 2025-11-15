"""Façade smoke tests for ΔΩ.149.D certification."""

from datetime import datetime, timezone

from core.spiral_api import (
    compute_system_status,
    evaluate_governance_event,
    get_current_scarindex,
    record_panic_frame,
)
from core.contracts.governance import GovernanceEvent, GovernanceStatus
from core.contracts.panicframes import PanicFrame, PanicFrameStatus
from core.contracts.scarindex import ScarIndexState
from core.contracts.system import SystemPulse


def _panic_frame_fixture() -> PanicFrame:
    """Construct a representative PanicFrame contract for smoke testing."""

    panic_status = PanicFrameStatus(
        state="ACTIVE",
        recovery_phase="PHASE_1_ASSESSMENT",
        escalation_level=1,
        acknowledged_by=["agent.zeta"],
        updated_at=datetime.now(timezone.utc),
    )

    return PanicFrame(
        id="panic-test",
        triggered_at=datetime.now(timezone.utc),
        scarindex_value=0.25,
        trigger_threshold=0.3,
        status=panic_status,
        frozen_operations=["scarcoin_mint", "vaultnode_gen"],
        metadata={"source": "test"},
    )


def _governance_event_fixture() -> GovernanceEvent:
    """Construct a representative GovernanceEvent contract."""

    return GovernanceEvent(
        id="gov-test",
        phase="ΔΩ.149",
        event_type="policy",
        submitted_at=datetime.now(timezone.utc),
        payload={"action": "update-threshold"},
        witnesses=["agent.alpha"],
        lineage_hash="abc123",
    )


def test_get_current_scarindex_smoke():
    state = get_current_scarindex()

    assert isinstance(state, ScarIndexState)

    payload = state.model_dump()
    assert payload["phase"].startswith("ΔΩ")
    assert isinstance(payload["value"], (int, float))
    assert payload["trend"] in {"up", "down", "stable"}
    assert "recorded_at" in payload
    assert isinstance(state.breakdown, list)
    if state.breakdown:
        component = state.breakdown[0]
        assert component.component
        assert isinstance(component.ache_value, float)


def test_record_panic_frame_smoke():
    event = _panic_frame_fixture()

    status = record_panic_frame(event)

    assert isinstance(status, PanicFrameStatus)

    payload = status.model_dump()
    assert payload["state"]
    assert isinstance(payload["escalation_level"], int)
    assert "updated_at" in payload
    assert isinstance(payload["acknowledged_by"], list)


def test_compute_system_status_smoke():
    pulse = compute_system_status()

    assert isinstance(pulse, SystemPulse)

    payload = pulse.model_dump()
    assert payload["captured_at"]
    assert payload["mode"] in {"panic-monitor", "operational"}
    assert isinstance(payload["scarindex_value"], (int, float))
    assert payload["panic_state"] in {"active", "clear"}
    assert isinstance(payload["health_score"], float)


def test_evaluate_governance_event_smoke():
    event = _governance_event_fixture()

    status = evaluate_governance_event(event)

    assert isinstance(status, GovernanceStatus)

    payload = status.model_dump()
    assert payload["event_id"] == event.id
    assert payload["decision"] in {"ACKNOWLEDGED", "PENDING"}
    assert payload["quorum"]
    assert "lineage_hash" in payload
