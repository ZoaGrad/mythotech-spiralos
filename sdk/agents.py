"""ΔΩ.150 Agent SDK utilities built on top of :mod:`core.agent_bridge`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence

from pydantic import BaseModel

from core.agent_bridge import AgentBridge
from core.agent_context import AgentContext
from core.contracts.governance import GovernanceEvent
from core.contracts.panicframes import PanicFrame


@dataclass(frozen=True)
class AgentResult:
    """Canonical SDK response with serialized context and payload."""

    contract: str
    payload: Dict[str, Any]
    context: Dict[str, Any]

    @classmethod
    def from_model(
        cls,
        *,
        contract: str,
        model: BaseModel,
        context: AgentContext,
    ) -> "AgentResult":
        return cls(contract=contract, payload=model.model_dump(), context=context.serialize())


def _build_context(
    *,
    agent_id: str,
    agent_version: str,
    session_id: str | None = None,
    lineage: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgentContext:
    return AgentContext.create(
        agent_id=agent_id,
        agent_version=agent_version,
        session_id=session_id,
        lineage=tuple(lineage or ()),
        metadata=metadata,
    )


def fetch_scar_index(
    *,
    agent_id: str,
    agent_version: str,
    session_id: str | None = None,
    lineage: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgentResult:
    """Retrieve the ScarIndex snapshot along with serialized context."""

    context = _build_context(
        agent_id=agent_id,
        agent_version=agent_version,
        session_id=session_id,
        lineage=lineage,
        metadata=metadata,
    )
    bridge = AgentBridge(context)
    state = bridge.get_scar_index()
    return AgentResult.from_model(contract="ScarIndexState", model=state, context=context)


def submit_panic_frame(
    *,
    agent_id: str,
    agent_version: str,
    event: PanicFrame,
    session_id: str | None = None,
    lineage: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgentResult:
    """Record a panic frame event through the bridge."""

    context = _build_context(
        agent_id=agent_id,
        agent_version=agent_version,
        session_id=session_id,
        lineage=lineage,
        metadata=metadata,
    )
    bridge = AgentBridge(context)
    status = bridge.record_panic_frame(event)
    return AgentResult.from_model(contract="PanicFrameStatus", model=status, context=context)


def fetch_system_status(
    *,
    agent_id: str,
    agent_version: str,
    session_id: str | None = None,
    lineage: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgentResult:
    """Fetch the SystemPulse contract via the bridge."""

    context = _build_context(
        agent_id=agent_id,
        agent_version=agent_version,
        session_id=session_id,
        lineage=lineage,
        metadata=metadata,
    )
    bridge = AgentBridge(context)
    pulse = bridge.compute_system_status()
    return AgentResult.from_model(contract="SystemPulse", model=pulse, context=context)


def evaluate_governance_event(
    *,
    agent_id: str,
    agent_version: str,
    event: GovernanceEvent,
    session_id: str | None = None,
    lineage: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> AgentResult:
    """Evaluate a governance event via the bridge."""

    context = _build_context(
        agent_id=agent_id,
        agent_version=agent_version,
        session_id=session_id,
        lineage=lineage,
        metadata=metadata,
    )
    bridge = AgentBridge(context)
    status = bridge.evaluate_governance_event(event)
    return AgentResult.from_model(contract="GovernanceStatus", model=status, context=context)
