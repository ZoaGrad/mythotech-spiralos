"""Storage adapters for the SpiraLOS event logger."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol
from uuid import uuid4


DEFAULT_STORAGE_PATH = Path.home() / ".spiralos" / "events.json"


class StorageProtocol(Protocol):
    """Protocol for storage backends used by :class:`EventLogger`."""

    def save_event(self, event_name: str, metadata: Dict) -> str:
        ...

    def get_events(self, limit: Optional[int] = None) -> Iterable[Dict]:
        ...

    def export_json(self, path: Path) -> None:
        ...

    def export_markdown(self, path: Path) -> None:
        ...


@dataclass
class JSONStorage:
    """Persist events as JSON on disk."""

    path: Path = DEFAULT_STORAGE_PATH

    def __post_init__(self) -> None:
        self.path = Path(self.path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_events([])

    def save_event(self, event_name: str, metadata: Dict) -> str:
        events = self._read_events()
        event_id = str(uuid4())
        event_record = {
            "id": event_id,
            "name": event_name,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        events.append(event_record)
        self._write_events(events)
        return event_id

    def get_events(self, limit: Optional[int] = None) -> Iterable[Dict]:
        events = list(reversed(self._read_events()))
        if limit is not None:
            return events[:limit]
        return events

    def export_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as destination:
            json.dump(list(self.get_events()), destination, indent=2)

    def export_markdown(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# SpiraLOS Event Log"]
        for event in self.get_events():
            lines.append(f"- **{event['timestamp']}** — {event['name']}")
            if event.get("metadata"):
                lines.append(f"  - metadata: {json.dumps(event['metadata'], ensure_ascii=False)}")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _read_events(self) -> List[Dict]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_events(self, events: List[Dict]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(events, handle, indent=2)
