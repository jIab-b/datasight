import os
import psycopg2
from pathlib import Path

root = Path(__file__).resolve().parent
schema_path = root / "schema.sql"

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/datasight")

with open(schema_path, "r", encoding="utf-8") as f:
	sql = f.read()

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute(sql)
conn.commit()
cur.close()
conn.close()

print("Database initialized successfully")
