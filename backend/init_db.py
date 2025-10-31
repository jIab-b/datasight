import os
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent
schema_path = root / "schema.sql"
db_path = os.getenv("SQLITE_PATH", str(root.parent / "datasight.db"))

with open(schema_path, "r", encoding="utf-8") as f:
	sql = f.read()

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.executescript(sql)
conn.commit()
cur.close()
conn.close()
