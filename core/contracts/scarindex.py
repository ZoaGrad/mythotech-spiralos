"""ΔΩ.149.B ScarIndex contract objects."""

from __future__ import annotations

from datetime import datetime, timezone
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

    def to_guardian_current(self, bridge_id: str) -> "GuardianScarIndexCurrent":
        """Align state with the guardian_scarindex_current schema."""

        return GuardianScarIndexCurrent(
            bridge_id=bridge_id,
            scar_value=self.value,
            metadata=self.metadata or {},
            updated_at=self.recorded_at,
        )

    def to_guardian_history(
        self,
        bridge_id: str,
        *,
        previous_value: float | None = None,
        source: str = "telemetry_normalize",
    ) -> "GuardianScarIndexHistory":
        """Map the ScarIndexState into the guardian_scarindex_history shape."""

        delta = self.value - (previous_value if previous_value is not None else self.value)

        return GuardianScarIndexHistory(
            bridge_id=bridge_id,
            scar_value=self.value,
            delta=delta,
            source=source,
            metadata={
                "lineage_hash": self.lineage_hash,
                "trend": self.trend,
                "phase": self.phase,
                **(self.metadata or {}),
            },
            timestamp=self.recorded_at,
        )


class GuardianScarIndexCurrent(BaseModel):
    """Schema-aligned view of guardian_scarindex_current."""

    bridge_id: str = Field(..., description="bridge_nodes.id that owns this ScarIndex")
    scar_value: float = Field(
        ..., ge=0.0, le=100.0, description="Latest ScarIndex value recorded for the bridge.",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Metadata persisted alongside the current ScarIndex value.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the latest ScarIndex update.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the current record was first created.",
    )


class GuardianScarIndexHistory(BaseModel):
    """Schema-aligned view of guardian_scarindex_history."""

    bridge_id: str = Field(..., description="bridge_nodes.id that owns this ScarIndex")
    scar_value: float = Field(..., ge=0.0, le=100.0, description="ScarIndex value at timestamp.")
    delta: float = Field(..., description="Change from previous value.")
    source: str = Field(
        default="telemetry_normalize",
        description="Source of the ScarIndex update (edge function or job).",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Audit metadata stored with the history row.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the ScarIndex observation was recorded.",
    )
