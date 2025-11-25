"""Schema definitions for the External Witness Telemetry stack."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .coercion import coerce_utc_timestamp


class ExternalWitnessEvent(BaseModel):
    """Normalized representation of an inbound external witness signal."""

    model_config = ConfigDict(extra="forbid")

    witness_id: str
    source: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signature: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    trust_score: Optional[float] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def _normalize_timestamp(cls, value: Any) -> datetime:
        return coerce_utc_timestamp(value)

    @field_validator("trust_score", mode="before")
    @classmethod
    def _clamp_trust_score(cls, value: Optional[float]) -> Optional[float]:
        if value is None:
            return value
        return max(0.0, min(1.0, value))


class ExternalQuarantineRecord(BaseModel):
    """Record persisted when an external signal fails validation."""

    model_config = ConfigDict(extra="forbid")

    reason: str
    raw_event: Dict[str, Any]
    detail: Optional[str] = None
    quarantined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("quarantined_at", mode="before")
    @classmethod
    def _normalize_quarantine_timestamp(cls, value: Any) -> datetime:
        return coerce_utc_timestamp(value)


__all__ = [
    "ExternalQuarantineRecord",
    "ExternalWitnessEvent",
]
