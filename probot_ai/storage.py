import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY, ts TEXT NOT NULL, kind TEXT NOT NULL,
                symbol TEXT, payload TEXT NOT NULL)""")

    def connect(self):
        return sqlite3.connect(self.path)

    def log(self, kind, payload, symbol=None):
        with self.connect() as con:
            con.execute("INSERT INTO events(ts,kind,symbol,payload) VALUES(?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), kind, symbol,
                 json.dumps(payload, default=str)))
