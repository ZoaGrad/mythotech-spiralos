"""ΔΩ.149.B ScarIndex contract objects."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ScarIndexBreakdown(BaseModel):
    """Represents a contributing factor to the ScarIndex trajectory."""

    component: str = Field(..., description="Name of the contributing μApp or metric.")
    ache_value: float = Field(..., ge=0.0, description="Ache mass attributed to this component.")
    ache_delta: float = Field(..., description="Change since the previous measurement.")
    weight: float = Field(..., description="Weight applied when composing the ScarIndex.")
    rationale: Optional[str] = Field(
        None,
        description="Narrative justification or Guardian note for audit lineage.",
    )


class ScarIndexState(BaseModel):
    """Canonical snapshot of the ScarIndex signal."""

    phase: str = Field(..., description="ΔΩ phase associated with this snapshot.")
    value: float = Field(..., description="Current ScarIndex value after normalization.")
    trend: str = Field(..., description="Directional trend such as up/down/flat.")
    recorded_at: datetime = Field(..., description="UTC timestamp of the capture event.")
    witness_id: str = Field(..., description="Identifier of the witnessing agent.")
    lineage_hash: str = Field(..., description="Audit hash linking to canonical lineage.")
    breakdown: List[ScarIndexBreakdown] = Field(
        default_factory=list,
        description="Component-level contributions to the ScarIndex value.",
    )
    metadata: Optional[dict] = Field(
        None,
        description="Optional metadata for kernels requiring auxiliary telemetry.",
    )
