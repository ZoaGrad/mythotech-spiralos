import json
from typing import Optional, Dict, Any
from .db import db as default_db, DatabaseWrapper

class ScarLockController:
    """
    Global constitutional lock controller.
    When engaged, structural/autopoietic mutations should halt.
    """

    def __init__(self, db: Optional[DatabaseWrapper] = None):
        self.db = db or default_db

    def _get_lock_row(self) -> Dict[str, Any]:
        res = self.db.client._ensure_client().table("constitutional_lock").select("*").limit(1).execute()
        if not res.data:
            # Should not happen if migration ran, but be defensive.
            self.db.client._ensure_client().table("constitutional_lock").insert({
                "is_locked": False,
                "reason": "auto_created",
                "created_by": "system"
            }).execute()
            res = self.db.client._ensure_client().table("constitutional_lock").select("*").limit(1).execute()
        return res.data[0]

    def is_locked(self) -> bool:
        row = self._get_lock_row()
        return bool(row["is_locked"])

    def engage_lock(self, reason: str, actor: str = "guardian") -> None:
        self.db.client._ensure_client().table("constitutional_lock").update({
            "is_locked": True,
            "reason": reason,
            "created_by": actor,
            "created_at": "now()",
            "released_at": None
        }).neq("id", "00000000-0000-0000-0000-000000000000").execute() # Update all rows (should be only 1)
        
        # Log event
        self.db.client._ensure_client().table("system_events").insert({
            "event_type": "LOCKDOWN_ENGAGED",
            "payload": {"reason": reason, "actor": actor}
        }).execute()

    def release_lock(self, actor: str = "guardian", resolution_note: str = "") -> None:
        self.db.client._ensure_client().table("constitutional_lock").update({
            "is_locked": False,
            "released_at": "now()"
        }).neq("id", "00000000-0000-0000-0000-000000000000").execute()

        self.db.client._ensure_client().table("system_events").insert({
            "event_type": "LOCKDOWN_RELEASED",
            "payload": {"actor": actor, "resolution": resolution_note}
        }).execute()

    def status(self) -> Dict[str, Any]:
        row = self._get_lock_row()
        return {
            "is_locked": bool(row["is_locked"]),
            "reason": row.get("reason"),
            "created_by": row.get("created_by"),
            "created_at": row.get("created_at"),
            "released_at": row.get("released_at"),
        }
