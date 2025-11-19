"""Airlock quarantine system for write access governance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class StateColor(Enum):
    GOLD = "SOVEREIGN"
    YELLOW = "TURBULENT"
    RED = "POISONED"


@dataclass
class ArchitectState:
    scar_index: float = 0.8
    is_under_lockdown: bool = False


class AirlockManager:
    """Simplified safety protocol gatekeeper."""

    def __init__(self):
        self.state = ArchitectState()

    def request_write_access(self, raw_input: str, context: Optional[Dict] = None) -> bool:
        if self.state.is_under_lockdown:
            return False
        if self.state.scar_index < 0.6:
            return False
        return True

    def set_state(self, scar_index: float, lockdown: bool = False) -> None:
        self.state.scar_index = scar_index
        self.state.is_under_lockdown = lockdown

    def status_color(self) -> StateColor:
        if self.state.is_under_lockdown or self.state.scar_index < 0.4:
            return StateColor.RED
        if self.state.scar_index < 0.6:
            return StateColor.YELLOW
        return StateColor.GOLD
