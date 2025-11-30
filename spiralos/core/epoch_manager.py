"""Simple EpochManager primitive for coordinating epoch ticks."""

from __future__ import annotations


class EpochManager:
    """Lightweight epoch tracker.

    This implementation provides minimal functionality for components that
    depend on a monotonically increasing epoch counter. Production systems may
    extend or replace this class with distributed timekeepers.
    """

    def __init__(self, current_epoch: int = 0):
        self._current_epoch = current_epoch

    def get_current_epoch(self) -> int:
        return self._current_epoch

    def advance_epoch(self) -> int:
        self._current_epoch += 1
        return self._current_epoch
