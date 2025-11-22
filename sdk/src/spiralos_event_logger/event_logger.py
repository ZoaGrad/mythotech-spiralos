"""Core event logger implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .storage import JSONStorage, StorageProtocol


class EventLogger:
    """Record events using a pluggable storage backend."""

    def __init__(self, storage: Optional[StorageProtocol] = None) -> None:
        self.storage = storage or JSONStorage()

    def log_event(self, event_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log an event and return its identifier."""

        event_id = self.storage.save_event(event_name, metadata or {})
        return event_id

    def retrieve_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve stored events ordered from newest to oldest."""

        return list(self.storage.get_events(limit=limit))

    def export_to_json(self, path: str | Path) -> None:
        """Export events to a JSON file at ``path``."""

        self.storage.export_json(Path(path))

    def export_to_markdown(self, path: str | Path) -> None:
        """Export events to a Markdown file at ``path``."""

        self.storage.export_markdown(Path(path))
