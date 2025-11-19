import os, sqlite3, time, json
SPIRAL_DATA_DIR = os.path.join(os.getcwd(), "spiral_data")
ECONOMY_DB_PATH = os.path.join(SPIRAL_DATA_DIR, "economy.db")
class ScarCoinMintingEngine:
    def __init__(self, db_path=ECONOMY_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE IF NOT EXISTS economy_meta (key TEXT PRIMARY KEY, value TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS mint_events (id INTEGER PRIMARY KEY, ts REAL, amount REAL, context TEXT)")
        self.conn.execute("INSERT OR IGNORE INTO economy_meta VALUES ('total_supply', '0')")
        self.conn.commit()
    @property
    def total_supply(self):
        row = self.conn.execute("SELECT value FROM economy_meta WHERE key='total_supply'").fetchone()
        return float(row['value']) if row else 0.0
    def mint(self, amount, context=None):
        self.conn.execute("INSERT INTO mint_events (ts, amount, context) VALUES (?, ?, ?)", (time.time(), amount, json.dumps(context)))
        new_total = self.total_supply + amount
        self.conn.execute("UPDATE economy_meta SET value=? WHERE key='total_supply'", (str(new_total),))
        self.conn.commit()
        return new_total
