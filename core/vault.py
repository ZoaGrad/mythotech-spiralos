"""Immutable system event logger stored inside SQLite."""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Iterable, Optional

SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
VAULT_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "vault.db")


@dataclass
class VaultEvent:
    id: int
    ts: float
    event_type: str
    delta: Optional[float]
    payload_json: Optional[str]
    meta_json: Optional[str]


class VaultEventLogger:
    """Append-only immutable event log."""

    def __init__(self, db_path: str = VAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS vault_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                event_type TEXT NOT NULL,
                delta REAL,
                payload_json TEXT,
                meta_json TEXT
            )
            """
        )
        self.conn.commit()

    def log_event(
        self,
        event_type: str,
        delta: Optional[float] = None,
        payload_json: Optional[str] = None,
        meta_json: Optional[str] = None,
    ) -> int:
        ts = time.time()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO vault_events (ts, event_type, delta, payload_json, meta_json) VALUES (?, ?, ?, ?, ?)",
            (ts, event_type, delta, payload_json, meta_json),
        )
        self.conn.commit()
        return cur.lastrowid

    def iter_events(self) -> Iterable[VaultEvent]:
        cur = self.conn.cursor()
        for row in cur.execute("SELECT * FROM vault_events ORDER BY id ASC"):
            yield VaultEvent(
                id=row["id"],
                ts=row["ts"],
                event_type=row["event_type"],
                delta=row["delta"],
                payload_json=row["payload_json"],
                meta_json=row["meta_json"],
            )

    def close(self) -> None:
        self.conn.close()
