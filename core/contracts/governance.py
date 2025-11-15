"""ΔΩ.149.B Governance contract objects."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GovernanceEvent(BaseModel):
    """Proposal or directive entering the Guardian review flow."""

    id: str = Field(..., description="Unique identifier for the governance event.")
    phase: str = Field(..., description="ΔΩ phase the event targets or originates from.")
    event_type: str = Field(..., description="Type label such as 'ritual', 'policy', or 'mutation'.")
    submitted_at: datetime = Field(..., description="Timestamp when the event was registered.")
    payload: Dict[str, object] = Field(
        default_factory=dict,
        description="Arbitrary payload describing the requested change.",
    )
    witnesses: List[str] = Field(
        default_factory=list,
        description="Witness identifiers tied to the submission.",
    )
    lineage_hash: Optional[str] = Field(
        None,
        description="Optional hash referencing supporting audit material.",
    )


class GovernanceStatus(BaseModel):
    """Current disposition of a governance event."""

    event_id: str = Field(..., description="Reference back to the GovernanceEvent identifier.")
    decision: str = Field(..., description="Outcome such as APPROVED, REJECTED, or ESCALATED.")
    decided_at: Optional[datetime] = Field(
        None,
        description="When the Guardian quorum finalized the decision.",
    )
    quorum: str = Field(..., description="Description of the quorum or council that decided the event.")
    notes: Optional[str] = Field(None, description="Supplementary Guardian commentary.")
    lineage_hash: Optional[str] = Field(
        None,
        description="Hash referencing the signed decision artifact.",
    )
