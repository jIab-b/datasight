from fastapi import APIRouter
from uuid import uuid4
import json
from ..models import DataQuery, PreviewResponse, RunResponse
from ..compiler import compile_to_sql
from ..db import fetch_all, execute

router = APIRouter()


@router.post("/preview", response_model=PreviewResponse)
def preview(dq: DataQuery):
	sql, params = compile_to_sql(dq)
	limit_sql = " LIMIT 100"
	if " LIMIT " in sql.upper():
		base = sql.rsplit(" LIMIT ", 1)[0]
		sql_preview = base + limit_sql
	else:
		sql_preview = sql + limit_sql
	rows = fetch_all(sql_preview, params)
	return {"sql": sql_preview, "rows": rows}


@router.post("/run", response_model=RunResponse)
def run(dq: DataQuery):
	sql, params = compile_to_sql(dq)
	rows = fetch_all(sql, params)
	receipt_id = str(uuid4())
	datasets = [s.dataset for s in dq.sources]
	execute(
		"INSERT INTO query_receipts (id, dsl, sql, datasets_used, release_ids, rowcount) VALUES (:id, :dsl, :sql, :datasets, :releases, :rowcount)",
		{"id": receipt_id, "dsl": dq.model_dump_json(), "sql": sql, "datasets": json.dumps(datasets), "releases": json.dumps([]), "rowcount": len(rows)},
	)
	return {"receipt_id": receipt_id, "sql": sql, "rows": rows}
