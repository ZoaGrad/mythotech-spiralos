"""ΔΩ.149.B: Internal API Contracts Bound. No logic implemented in this phase.

ΔΩ.149.A — SpiralOS Internal API Façade (Skeleton)
"""

from core.contracts.governance import GovernanceEvent, GovernanceStatus
from core.contracts.panicframes import PanicFrame, PanicFrameStatus
from core.contracts.scarindex import ScarIndexState
from core.contracts.system import SystemPulse


def get_current_scarindex() -> ScarIndexState:
    """Return the latest ScarIndex snapshot.
    ΔΩ.149.A — façade only, no logic yet.
    """
    raise NotImplementedError


def record_panic_frame(event: PanicFrame) -> PanicFrameStatus:
    """Record a panic frame event through the façade.
    ΔΩ.149.A — façade only.
    """
    raise NotImplementedError


def compute_system_status() -> SystemPulse:
    """Compute a high-level system status report.
    ΔΩ.149.A — façade only.
    """
    raise NotImplementedError


def evaluate_governance_event(event: GovernanceEvent) -> GovernanceStatus:
    """Evaluate a governance event and return the decision.
    ΔΩ.149.A — façade only.
    """
    raise NotImplementedError
