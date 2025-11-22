"""Agent context primitives for ΔΩ.150 agent integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple
from spiral_types import MappingProxyType
from uuid import uuid4


@dataclass(frozen=True)
class AgentContext:
    """Immutable metadata passed to each agent bridge invocation."""

    agent_id: str
    agent_version: str
    session_id: str
    request_id: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    lineage: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def create(
        cls,
        *,
        agent_id: str,
        agent_version: str,
        session_id: str | None = None,
        request_id: str | None = None,
        lineage: Tuple[str, ...] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "AgentContext":
        """Instantiate a context with generated identifiers where needed."""

        session = session_id or str(uuid4())
        req = request_id or str(uuid4())
        issued_at = datetime.now(timezone.utc)
        frozen_metadata: Mapping[str, Any] = MappingProxyType(dict(metadata or {}))
        safe_lineage = tuple(lineage or ())
        return cls(
            agent_id=agent_id,
            agent_version=agent_version,
            session_id=session,
            request_id=req,
            issued_at=issued_at,
            lineage=safe_lineage,
            metadata=frozen_metadata,
        )

    def serialize(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the context."""

        return {
            "agent_id": self.agent_id,
            "agent_version": self.agent_version,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "issued_at": self.issued_at.isoformat(),
            "lineage": list(self.lineage),
            "metadata": dict(self.metadata),
        }
