"""ΔΩ.150 agent integration smoke tests."""

from __future__ import annotations

from datetime import datetime, timezone

from core.agent_bridge import AgentBridge
from core.agent_context import AgentContext
from core.contracts.governance import GovernanceEvent, GovernanceStatus
from core.contracts.panicframes import PanicFrame, PanicFrameStatus
from core.contracts.scarindex import ScarIndexState
from core.contracts.system import SystemPulse
from sdk import (
    AgentResult,
    evaluate_governance_event as sdk_evaluate_governance_event,
    fetch_scar_index,
    fetch_system_status,
    submit_panic_frame,
)


def _panic_frame_fixture() -> PanicFrame:
    status = PanicFrameStatus(
        state="ACTIVE",
        recovery_phase="PHASE_1_ASSESSMENT",
        escalation_level=1,
        acknowledged_by=["agent.tester"],
        updated_at=datetime.now(timezone.utc),
    )

    return PanicFrame(
        id="panic-agent-test",
        triggered_at=datetime.now(timezone.utc),
        scarindex_value=0.42,
        trigger_threshold=0.5,
        status=status,
        frozen_operations=["vault_lock"],
        metadata={"source": "agent"},
    )


def _governance_event_fixture() -> GovernanceEvent:
    return GovernanceEvent(
        id="gov-agent-test",
        phase="ΔΩ.150",
        event_type="policy",
        submitted_at=datetime.now(timezone.utc),
        payload={"action": "stabilize"},
        witnesses=["agent.tester"],
        lineage_hash="lineage-test",
    )


def test_agent_context_serialization_stable():
    context = AgentContext.create(
        agent_id="agent.delta",
        agent_version="1.2.3",
        session_id="session-123",
        request_id="req-456",
        lineage=("root", "child"),
        metadata={"channel": "discord"},
    )

    payload = context.serialize()
    assert payload["agent_id"] == "agent.delta"
    assert payload["session_id"] == "session-123"
    assert payload["request_id"] == "req-456"
    assert payload["lineage"] == ["root", "child"]
    assert payload["metadata"] == {"channel": "discord"}
    assert payload["issued_at"].endswith("+00:00")


def test_agent_bridge_returns_contract_types():
    context = AgentContext.create(agent_id="agent.delta", agent_version="1.0.0")
    bridge = AgentBridge(context)
    panic_event = _panic_frame_fixture()
    gov_event = _governance_event_fixture()

    scarindex_state = bridge.get_scar_index()
    assert isinstance(scarindex_state, ScarIndexState)

    panic_status = bridge.record_panic_frame(panic_event)
    assert isinstance(panic_status, PanicFrameStatus)

    pulse = bridge.compute_system_status()
    assert isinstance(pulse, SystemPulse)

    governance_status = bridge.evaluate_governance_event(gov_event)
    assert isinstance(governance_status, GovernanceStatus)


def test_sdk_helpers_return_agent_result():
    scarindex_result = fetch_scar_index(agent_id="agent.delta", agent_version="1.0.0")
    assert isinstance(scarindex_result, AgentResult)
    assert scarindex_result.contract == "ScarIndexState"
    assert scarindex_result.context["agent_id"] == "agent.delta"
    assert "phase" in scarindex_result.payload

    panic_event = _panic_frame_fixture()
    panic_result = submit_panic_frame(
        agent_id="agent.delta",
        agent_version="1.0.0",
        event=panic_event,
        metadata={"intent": "test"},
    )
    assert panic_result.contract == "PanicFrameStatus"
    assert panic_result.context["metadata"] == {"intent": "test"}

    gov_event = _governance_event_fixture()
    gov_result = sdk_evaluate_governance_event(
        agent_id="agent.delta",
        agent_version="1.0.0",
        event=gov_event,
    )
    assert gov_result.contract == "GovernanceStatus"
    assert gov_result.payload["event_id"] == gov_event.id

    pulse_result = fetch_system_status(agent_id="agent.delta", agent_version="1.0.0")
    assert pulse_result.contract == "SystemPulse"
    assert "mode" in pulse_result.payload
