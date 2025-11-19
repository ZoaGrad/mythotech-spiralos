import os, sqlite3, time, json
VAULT_DB_PATH = os.path.join(os.getcwd(), "spiral_data", "vault.db")
class VaultEventLogger:
    def __init__(self, db_path=VAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS vault_events (id INTEGER PRIMARY KEY, ts REAL, event_type TEXT, payload_json TEXT)")
        self._migrate_schema()
        self.conn.commit()
    
    def _migrate_schema(self):
        """Migrate old schema to new schema with event_type and payload_json columns"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(vault_events)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'event_type' not in columns and 'type' in columns:
            # Old schema detected - need to recreate table
            try:
                # Rename old table
                self.conn.execute("ALTER TABLE vault_events RENAME TO vault_events_old")
                # Create new table with correct schema
                self.conn.execute("CREATE TABLE vault_events (id INTEGER PRIMARY KEY, ts REAL, event_type TEXT, payload_json TEXT)")
                # Migrate data
                self.conn.execute("INSERT INTO vault_events (id, ts, event_type, payload_json) SELECT id, ts, type, payload FROM vault_events_old")
                # Drop old table
                self.conn.execute("DROP TABLE vault_events_old")
            except sqlite3.OperationalError:
                pass
    
    def log_event(self, event_type, payload):
        self.conn.execute("INSERT INTO vault_events (ts, event_type, payload_json) VALUES (?, ?, ?)", (time.time(), event_type, json.dumps(payload)))
        self.conn.commit()
