"""Simple routing layer for the unified telemetry bus."""

from __future__ import annotations

from typing import Callable, Dict, Mapping

Handler = Callable[[Mapping[str, object]], object]


class TelemetryRouter:
    def __init__(self) -> None:
        self._handlers: Dict[str, Handler] = {}

    def register(self, kind: str, handler: Handler) -> None:
        self._handlers[kind] = handler

    def route(self, kind: str, payload: Mapping[str, object]):
        if kind not in self._handlers:
            raise KeyError(f"No handler registered for telemetry kind '{kind}'")
        return self._handlers[kind](payload)

    def registered_kinds(self) -> list[str]:
        return sorted(self._handlers)


__all__ = ["TelemetryRouter", "Handler"]
