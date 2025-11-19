"""Persistent ScarCoin minting engine backed by SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Union

SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
ECONOMY_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "economy.db")


@dataclass
class MintEvent:
    """Representation of a stored mint event."""

    id: int
    ts: float
    amount: float
    delta: float
    reason: Optional[str]
    context_json: Optional[str]


class ScarCoinMintingEngine:
    """SQLite-backed persistence layer for ScarCoin supply."""

    def __init__(self, db_path: str = ECONOMY_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS economy_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mint_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                amount REAL NOT NULL,
                delta REAL NOT NULL,
                reason TEXT,
                context_json TEXT
            )
            """
        )
        cur.execute("INSERT OR IGNORE INTO economy_meta (key, value) VALUES ('total_supply', '0')")
        self.conn.commit()

    @property
    def total_supply(self) -> float:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM economy_meta WHERE key = 'total_supply'")
        row = cur.fetchone()
        return float(row["value"]) if row else 0.0

    def mint(
        self,
        amount: float,
        delta: float,
        reason: Optional[str] = None,
        context: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> int:
        if amount <= 0:
            return 0
        ts = time.time()
        context_json = self._serialize_context(context)
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO mint_events (ts, amount, delta, reason, context_json) VALUES (?, ?, ?, ?, ?)",
            (ts, float(amount), float(delta), reason, context_json),
        )
        event_id = cur.lastrowid
        new_total = self.total_supply + float(amount)
        cur.execute("UPDATE economy_meta SET value = ? WHERE key = 'total_supply'", (str(new_total),))
        self.conn.commit()
        return event_id

    def iter_mint_events(self) -> Iterable[MintEvent]:
        cur = self.conn.cursor()
        for row in cur.execute("SELECT * FROM mint_events ORDER BY id ASC"):
            yield MintEvent(
                id=row["id"],
                ts=row["ts"],
                amount=row["amount"],
                delta=row["delta"],
                reason=row["reason"],
                context_json=row["context_json"],
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_supply": self.total_supply,
            "events": [event.__dict__ for event in self.iter_mint_events()],
        }

    def close(self) -> None:
        self.conn.close()

    def _serialize_context(self, context: Optional[Union[str, Dict[str, Any]]]) -> Optional[str]:
        if context is None:
            return None
        if isinstance(context, str):
            return context
        return json.dumps(context)
