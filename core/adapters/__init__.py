"""ΔΩ.149.C adapter helpers bridging runtime modules to contract façades."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from core.f2_judges import JudicialSystem
from core.spiralos import SpiralOS


@lru_cache()
def _get_spiralos() -> SpiralOS:
    """Instantiate SpiralOS once for adapter snapshots."""

    return SpiralOS(enable_consensus=False, enable_panic_frames=True)


def get_spiralos_status() -> Dict[str, Any]:
    """Return the latest cached SpiralOS status snapshot."""

    return _get_spiralos().get_system_status()


@lru_cache()
def _get_judicial_system() -> JudicialSystem:
    """Create the ΔΩ judicial system singleton used for governance views."""

    return JudicialSystem()


def get_judicial_status() -> Dict[str, Any]:
    """Return the most recent Judicial system telemetry."""

    return _get_judicial_system().get_system_status()
