import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

_db_path = None


def init_pool() -> None:
	global _db_path
	root = Path(__file__).resolve().parents[2]
	_db_path = os.getenv("SQLITE_PATH", str(root / "datasight.db"))
	Path(_db_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def connection():
	conn = sqlite3.connect(_db_path, check_same_thread=False)
	conn.row_factory = sqlite3.Row
	try:
		yield conn
	finally:
		conn.close()


def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
	with connection() as conn:
		cur = conn.cursor()
		cur.execute(sql, params or {})
		rows = cur.fetchall()
		return [dict(r) for r in rows]


def fetch_one(sql: str, params: dict | None = None) -> dict | None:
	with connection() as conn:
		cur = conn.cursor()
		cur.execute(sql, params or {})
		row = cur.fetchone()
		return dict(row) if row else None


def execute(sql: str, params: dict | None = None) -> None:
	with connection() as conn:
		cur = conn.cursor()
		cur.execute(sql, params or {})
		conn.commit()
