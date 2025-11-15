"""AgentBridge delegates agent calls to the ΔΩ.149 façade."""

from __future__ import annotations

from core.agent_context import AgentContext
from core.contracts.governance import GovernanceEvent, GovernanceStatus
from core.contracts.panicframes import PanicFrame, PanicFrameStatus
from core.contracts.scarindex import ScarIndexState
from core.contracts.system import SystemPulse
from core.spiral_api import (
    compute_system_status,
    evaluate_governance_event,
    get_current_scarindex,
    record_panic_frame,
)


class AgentBridge:
    """Read-only façade wrapper that preserves an :class:`AgentContext`."""

    def __init__(self, context: AgentContext):
        self._context = context

    @property
    def context(self) -> AgentContext:
        """Return the immutable context used for the invocation."""

        return self._context

    def get_scar_index(self) -> ScarIndexState:
        """Return the latest ScarIndex contract."""

        return get_current_scarindex()

    def record_panic_frame(self, event: PanicFrame) -> PanicFrameStatus:
        """Pass through to the panic frame façade entrypoint."""

        return record_panic_frame(event)

    def compute_system_status(self) -> SystemPulse:
        """Return the latest SystemPulse contract."""

        return compute_system_status()

    def evaluate_governance_event(self, event: GovernanceEvent) -> GovernanceStatus:
        """Return the governance status computed by the façade."""

        return evaluate_governance_event(event)
