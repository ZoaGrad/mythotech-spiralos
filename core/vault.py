import os, sqlite3, time, json, hashlib
VAULT_DB_PATH = os.path.join(os.getcwd(), "spiral_data", "vault.db")
class VaultEventLogger:
    def __init__(self, db_path=VAULT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS vault_events (id INTEGER PRIMARY KEY, ts REAL, event_type TEXT, payload_json TEXT, neural_signature TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS neural_graph (id INTEGER PRIMARY KEY, parent_sig TEXT, child_sig TEXT, ts REAL)")
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
                self.conn.execute("CREATE TABLE vault_events (id INTEGER PRIMARY KEY, ts REAL, event_type TEXT, payload_json TEXT, neural_signature TEXT)")
                # Migrate data
                self.conn.execute("INSERT INTO vault_events (id, ts, event_type, payload_json) SELECT id, ts, type, payload FROM vault_events_old")
                # Drop old table
                self.conn.execute("DROP TABLE vault_events_old")
            except sqlite3.OperationalError:
                pass
        
        if 'neural_signature' not in columns:
            # Add neural_signature column
            try:
                self.conn.execute("ALTER TABLE vault_events ADD COLUMN neural_signature TEXT")
                # Generate signatures for existing records
                cursor.execute("SELECT id, ts, event_type FROM vault_events WHERE neural_signature IS NULL")
                for row in cursor.fetchall():
                    sig = hashlib.sha256(f"{row[2]}{row[1]}0".encode()).hexdigest()
                    self.conn.execute("UPDATE vault_events SET neural_signature = ? WHERE id = ?", (sig, row[0]))
            except sqlite3.OperationalError:
                pass
    
    def log_event(self, event_type, payload):
        ts = time.time()
        # Generate neural signature from event_type + timestamp + delta (0 if not in payload)
        delta = payload.get('delta', 0) if isinstance(payload, dict) else 0
        neural_signature = hashlib.sha256(f"{event_type}{ts}{delta}".encode()).hexdigest()
        
        # Get previous signature
        prev_sig = None
        cursor = self.conn.cursor()
        cursor.execute("SELECT neural_signature FROM vault_events ORDER BY ts DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0]:
            prev_sig = row[0]
        # Insert event
        self.conn.execute("INSERT INTO vault_events (ts, event_type, payload_json, neural_signature) VALUES (?, ?, ?, ?)", 
                         (ts, event_type, json.dumps(payload), neural_signature))
        # Insert neural_graph link
        self.conn.execute("INSERT INTO neural_graph (parent_sig, child_sig, ts) VALUES (?, ?, ?)", (prev_sig, neural_signature, ts))
        self.conn.commit()
