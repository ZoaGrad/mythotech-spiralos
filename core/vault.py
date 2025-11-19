import os, sqlite3, time, json
VAULT_DB_PATH = os.path.join(os.getcwd(), "spiral_data", "vault.db")
class VaultEventLogger:
    def __init__(self, db_path=VAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS vault_events (id INTEGER PRIMARY KEY, ts REAL, type TEXT, payload TEXT)")
        self.conn.commit()
    def log_event(self, event_type, payload):
        self.conn.execute("INSERT INTO vault_events (ts, type, payload) VALUES (?, ?, ?)", (time.time(), event_type, json.dumps(payload)))
        self.conn.commit()
