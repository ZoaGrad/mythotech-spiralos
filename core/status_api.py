from typing import Dict, Any, Optional
from .db import db as default_db, DatabaseWrapper
import json

class StatusAPI:
    """
    Core interface for the SpiralOS Status API.
    Wraps the `fn_status_api` RPC call.
    """
    def __init__(self, db: Optional[DatabaseWrapper] = None):
        self.db = db or default_db

    def get_status(self) -> Dict[str, Any]:
        """
        Fetch the global system status.
        Returns a dictionary containing lock_status, latest_event, and guardian_vows.
        """
        try:
            res = self.db.client._ensure_client().rpc("fn_status_api", {}).execute()
            if res.data:
                return res.data
            return {}
        except Exception as e:
            # Log error or re-raise depending on policy. For now, print and return empty.
            print(f"[StatusAPI] Error fetching status: {e}")
            return {}
