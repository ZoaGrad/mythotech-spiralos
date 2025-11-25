"""Rhythm governance constants for heartbeats and ScarIndex.

Phase-11 codifies freshness bounds in a single location so downstream CLI
checks, diagnostics, and adapters cannot drift.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RhythmBounds:
    label: str
    max_staleness_seconds: int


HEARTBEAT_BOUNDS = RhythmBounds(
    label="guardian_heartbeats",
    max_staleness_seconds=60 * 60,  # 1 hour
)

SCARINDEX_BOUNDS = RhythmBounds(
    label="guardian_scarindex_history",
    max_staleness_seconds=2 * 60 * 60,  # 2 hours to allow processing slack
)

__all__ = [
    "HEARTBEAT_BOUNDS",
    "SCARINDEX_BOUNDS",
    "RhythmBounds",
]
