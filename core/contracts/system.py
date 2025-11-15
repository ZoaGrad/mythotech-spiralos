"""ΔΩ.149.B System pulse contract."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SystemPulse(BaseModel):
    """High-level system health report used by the façade."""

    captured_at: datetime = Field(..., description="UTC timestamp for the pulse measurement.")
    mode: str = Field(..., description="Operating mode such as ritual-active or sealed-observer.")
    scarindex_value: float = Field(..., description="ScarIndex magnitude at capture time.")
    panic_state: str = Field(..., description="Summarized Panic Frame state.")
    governance_phase: str = Field(..., description="ΔΩ governance phase driving the system posture.")
    health_score: float = Field(..., description="Composite health metric normalized between 0 and 1.")
    notes: Optional[str] = Field(None, description="Optional free-form commentary for operators.")
