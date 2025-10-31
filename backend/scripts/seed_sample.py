import os
import csv
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parents[2]
price_csv = root / "sample_data" / "aemo_price_daily.csv"
demand_csv = root / "sample_data" / "aemo_demand_daily.csv"
db_path = os.getenv("SQLITE_PATH", str(root / "datasight.db"))

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("insert or ignore into datasets (id, name, topic) values (?,?,?)", ("aemo_price_daily", "AEMO Price Daily", "electricity"))
cur.execute("insert or ignore into datasets (id, name, topic) values (?,?,?)", ("aemo_demand_daily", "AEMO Demand Daily", "electricity"))
cur.execute("insert into dataset_releases (dataset_id, version) values (?, ?) on conflict(dataset_id, version) do nothing", ("aemo_price_daily", "sample"))
cur.execute("select id from dataset_releases where dataset_id=? and version=?", ("aemo_price_daily", "sample"))
release_price = cur.fetchone()[0]
cur.execute("insert into dataset_releases (dataset_id, version) values (?, ?) on conflict(dataset_id, version) do nothing", ("aemo_demand_daily", "sample"))
cur.execute("select id from dataset_releases where dataset_id=? and version=?", ("aemo_demand_daily", "sample"))
release_demand = cur.fetchone()[0]

cur.execute("delete from fact_price_daily where release_id=?", (release_price,))
cur.execute("delete from fact_demand_daily where release_id=?", (release_demand,))

with open(price_csv, newline="", encoding="utf-8") as f:
	reader = csv.DictReader(f)
	rows = [(r["date"], r["region"], float(r["price_mwh"]), release_price) for r in reader]
	cur.executemany("insert into fact_price_daily (date, region, price_mwh, release_id) values (?,?,?,?)", rows)

with open(demand_csv, newline="", encoding="utf-8") as f:
	reader = csv.DictReader(f)
	rows = [(r["date"], r["region"], float(r["demand_mw"]), release_demand) for r in reader]
	cur.executemany("insert into fact_demand_daily (date, region, demand_mw, release_id) values (?,?,?,?)", rows)

cur.execute("delete from fields where dataset_id=?", ("aemo_price_daily",))
cur.execute("delete from fields where dataset_id=?", ("aemo_demand_daily",))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_price_daily","date","date",None,"time"))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_price_daily","region","text",None,"geo"))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_price_daily","price_mwh","numeric","AUD/MWh","metric"))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_demand_daily","date","date",None,"time"))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_demand_daily","region","text",None,"geo"))
cur.execute("insert into fields (dataset_id, name, dtype, unit, semantic_role) values (?,?,?,?,?)", ("aemo_demand_daily","demand_mw","numeric","MW","metric"))

conn.commit()
cur.close()
conn.close()
