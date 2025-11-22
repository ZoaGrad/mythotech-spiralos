"""Read-only governance adapter exposing Oracle Council posture via contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.contracts.governance import GovernanceEvent, GovernanceStatus
from core.oracle_council import OracleCouncil, ProviderType


def to_governance_status(event: Optional[GovernanceEvent] = None) -> GovernanceStatus:
    """Project Oracle Council readiness into the GovernanceStatus contract."""

    council = OracleCouncil()
    providers = [oracle.provider for oracle in council.oracles.values()]
    non_commercial_present = any(
        oracle.provider_type == ProviderType.NON_COMMERCIAL for oracle in council.oracles.values()
    )

    quorum = f"{OracleCouncil.MIN_QUORUM}-of-{len(providers)} quorum ({', '.join(providers)})"
    decision = "ACKNOWLEDGED" if event else "PENDING"
    decided_at = datetime.now(timezone.utc) if event else None
    notes = (
        "Sentinels aligned; quorum satisfied."
        if non_commercial_present
        else "Constitutional warning: non-commercial provider missing."
    )

    return GovernanceStatus(
        event_id=event.id if event else "ΔΩ.149.C-governance-sync",
        decision=decision,
        decided_at=decided_at,
        quorum=quorum,
        notes=notes,
        lineage_hash=(event.lineage_hash if event and event.lineage_hash else ",".join(providers)),
    )
