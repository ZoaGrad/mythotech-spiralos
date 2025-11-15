"""ΔΩ.149.B Panic Frame contract objects."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PanicFrameStatus(BaseModel):
    """Describes the lifecycle posture of a Panic Frame."""

    state: str = Field(..., description="Human-readable state such as ACTIVE or RESOLVED.")
    recovery_phase: Optional[str] = Field(
        None,
        description="Current phase of the 7-stage recovery ritual, if applicable.",
    )
    escalation_level: int = Field(..., ge=0, description="Guardian escalation tier applied.")
    acknowledged_by: List[str] = Field(
        default_factory=list,
        description="Witness identifiers that acknowledged the frame.",
    )
    updated_at: datetime = Field(..., description="Timestamp of the latest status change.")


class PanicFrame(BaseModel):
    """Canonical Panic Frame signal exchanged through the façade."""

    id: str = Field(..., description="Unique identifier for the Panic Frame event.")
    triggered_at: datetime = Field(..., description="When the panic condition was detected.")
    scarindex_value: float = Field(..., description="ScarIndex reading at trigger time.")
    trigger_threshold: float = Field(..., description="Threshold that was crossed to trigger the frame.")
    status: PanicFrameStatus = Field(..., description="Current status of the Panic Frame.")
    frozen_operations: List[str] = Field(
        default_factory=list,
        description="Operations frozen while the Panic Frame is active.",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Supplementary payload for Supabase persistence or analytics.",
    )
