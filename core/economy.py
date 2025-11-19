import os
import sqlite3
import time
import json
from typing import Optional, Dict, Any

SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
ECONOMY_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "economy.db")

class ScarCoinMintingEngine:
    def __init__(self, db_path: str = ECONOMY_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS economy_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mint_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                amount REAL NOT NULL,
                delta REAL NOT NULL,
                reason TEXT,
                context_json TEXT
            )
        """)
        cur.execute("INSERT OR IGNORE INTO economy_meta (key, value) VALUES ('total_supply', '0')")
        self.conn.commit()

    @property
    def total_supply(self) -> float:
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM economy_meta WHERE key = 'total_supply'")
        row = cur.fetchone()
        return float(row["value"]) if row else 0.0

    def mint(self, amount: float, delta: float, reason: str = None, context_json: str = None) -> int:
        if amount <= 0: return 0
        ts = time.time()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO mint_events (ts, amount, delta, reason, context_json) VALUES (?, ?, ?, ?, ?)",
            (ts, float(amount), float(delta), reason, context_json)
        )
        event_id = cur.lastrowid
        new_total = self.total_supply + float(amount)
        cur.execute("UPDATE economy_meta SET value = ? WHERE key = 'total_supply'", (str(new_total),))
        self.conn.commit()
        return event_id
