"""Compatibility shim exposing the Airlock governance gate at the module root."""

from __future__ import annotations

from core.governance.airlock import AirlockManager, ArchitectState, StateColor

__all__ = ["AirlockManager", "ArchitectState", "StateColor"]
