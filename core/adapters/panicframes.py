"""Read-only Panic Frame adapter translating runtime data into contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.contracts.panicframes import PanicFrame, PanicFrameStatus
from core.panic_frames import PanicFrameEvent, get_panic_manager


def _convert_event(event: PanicFrameEvent) -> PanicFrameStatus:
    return PanicFrameStatus(
        state=event.status.value,
        recovery_phase=event.recovery_phase.name if event.recovery_phase else None,
        escalation_level=event.escalation_level,
        acknowledged_by=[],
        updated_at=event.resolved_at or event.triggered_at,
    )


def to_panic_frame_status(event: Optional[PanicFrame] = None) -> PanicFrameStatus:
    """Return the most relevant Panic Frame status without mutating runtime state."""

    manager = get_panic_manager()
    active_frames = manager.get_active_frames()

    if event:
        matching = next((frame for frame in active_frames if frame.id == event.id), None)
        if matching:
            return _convert_event(matching)

    if active_frames:
        latest = max(active_frames, key=lambda frame: frame.triggered_at)
        return _convert_event(latest)

    if event:
        # Fall back to the provided contract data; ensures deterministic echo.
        status = event.status
        return PanicFrameStatus(
            state=status.state,
            recovery_phase=status.recovery_phase,
            escalation_level=status.escalation_level,
            acknowledged_by=status.acknowledged_by,
            updated_at=status.updated_at,
        )

    return PanicFrameStatus(
        state="STANDBY",
        recovery_phase=None,
        escalation_level=0,
        acknowledged_by=[],
        updated_at=datetime.now(timezone.utc),
    )
