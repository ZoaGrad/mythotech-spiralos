import os, sqlite3, time, json
SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
ECONOMY_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "economy.db")
class ScarCoinMintingEngine:
    def __init__(self, db_path=ECONOMY_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE IF NOT EXISTS economy_meta (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS mint_events (id INTEGER PRIMARY KEY, ts REAL, amount REAL, reason TEXT, context TEXT)")
        self.conn.execute("INSERT OR IGNORE INTO economy_meta VALUES ('total_supply', '0')")
        self._migrate_schema()
        self.conn.commit()
    
    def _migrate_schema(self):
        """Migrate old schema to new schema with reason column"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(mint_events)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'reason' not in columns:
            # Old schema detected - add reason column
            try:
                self.conn.execute("ALTER TABLE mint_events ADD COLUMN reason TEXT DEFAULT 'Legacy transmutation'")
                # Update existing records to extract reason from context
                self.conn.execute("""
                    UPDATE mint_events 
                    SET reason = COALESCE(
                        json_extract(context, '$.source'),
                        json_extract(context, '$.reason'),
                        'Legacy transmutation'
                    )
                    WHERE reason IS NULL OR reason = 'Legacy transmutation'
                """)
            except sqlite3.OperationalError:
                # Column might already exist in some cases
                pass
    @property
    def total_supply(self):
        row = self.conn.execute("SELECT value FROM economy_meta WHERE key='total_supply'").fetchone()
        return float(row['value']) if row else 0.0
    def mint(self, amount, context=None):
        # Extract reason from context if available, otherwise use default
        reason = "Ache transmutation"
        if context:
            if isinstance(context, dict):
                reason = context.get('source', context.get('reason', 'Ache transmutation'))
            elif isinstance(context, str):
                reason = context
        self.conn.execute("INSERT INTO mint_events (ts, amount, reason, context) VALUES (?, ?, ?, ?)", 
                         (time.time(), amount, reason, json.dumps(context)))
        new_total = self.total_supply + amount
        self.conn.execute("UPDATE economy_meta SET value=? WHERE key='total_supply'", (str(new_total),))
        self.conn.commit()
        return new_total
