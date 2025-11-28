from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from .db import db as default_db, DatabaseWrapper

@dataclass
class CustodyEntry:
    entity: str
    permission_set: Dict[str, Any]
    active: bool

class CustodyRegistry:
    def __init__(self, db: Optional[DatabaseWrapper] = None):
        self.db = db or default_db

    def get_entry(self, entity: str) -> Optional[CustodyEntry]:
        # Using db wrapper's client to execute query
        res = self.db.client._ensure_client().table("custody_registry").select("entity, permission_set, active").eq("entity", entity).execute()
        if not res.data:
            return None
        row = res.data[0]
        return CustodyEntry(
            entity=row["entity"],
            permission_set=row["permission_set"],
            active=row["active"],
        )

    def has_permission(self, entity: str, permission: str) -> bool:
        entry = self.get_entry(entity)
        if not entry or not entry.active:
            return False
        return bool(entry.permission_set.get(permission, False))

    def list_active(self) -> List[CustodyEntry]:
        res = self.db.client._ensure_client().table("custody_registry").select("entity, permission_set, active").eq("active", True).execute()
        return [
            CustodyEntry(
                entity=r["entity"],
                permission_set=r["permission_set"],
                active=r["active"],
            )
            for r in res.data
        ]
