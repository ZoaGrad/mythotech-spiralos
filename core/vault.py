import os
import sqlite3
import time
import json
from typing import Optional

SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
VAULT_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "vault.db")

class VaultEventLogger:
    def __init__(self, db_path: str = VAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                event_type TEXT NOT NULL,
                delta REAL,
                payload_json TEXT,
                meta_json TEXT
            )
        """)
        self.conn.commit()

    def log_event(self, event_type: str, delta: float = None, payload_json: str = None, meta_json: str = None) -> int:
        ts = time.time()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO vault_events (ts, event_type, delta, payload_json, meta_json) VALUES (?, ?, ?, ?, ?)",
            (ts, event_type, delta, payload_json, meta_json)
        )
        self.conn.commit()
        return cur.lastrowid
