from .models import DataQuery


def _sql_lit(v):
	if v is None:
		return "NULL"
	if isinstance(v, (int, float)):
		return str(v)
	return "'" + str(v).replace("'", "''") + "'"


def compile_to_sql(dq: DataQuery) -> tuple[str, dict]:
	ctes: list[str] = []
	params: dict = {}
	for i, src in enumerate(dq.sources):
		where_clauses: list[str] = []
		if src.where:
			for k, v in src.where.items():
				key = f"{k}_{i}"
				if isinstance(v, list):
					vals = ",".join(_sql_lit(x) for x in v)
					where_clauses.append(f"{k} IN ({vals})")
				else:
					params[key] = v
					where_clauses.append(f"{k} = :{key}")
		if src.time:
			if "start" in src.time:
				params[f"start_{i}"] = src.time["start"]
				where_clauses.append(f"date >= :start_{i}")
			if "end" in src.time:
				params[f"end_{i}"] = src.time["end"]
				where_clauses.append(f"date <= :end_{i}")
		wc = " AND ".join(where_clauses) if where_clauses else "1=1"
		select_list = ", ".join(src.select)
		ctes.append(f"s{i} AS (SELECT {select_list} FROM {src.dataset} WHERE {wc})")
	with_clause = ("WITH " + ", ".join(ctes)) if ctes else ""
	if len(dq.sources) == 1:
		base = "SELECT * FROM s0"
	else:
		on = []
		if dq.join and isinstance(dq.join.get("on"), list):
			on = dq.join["on"]
		join_cond = " AND ".join([f"s0.{k}=s1.{k}" for k in on]) if on else "1=1"
		base = f"SELECT * FROM s0 JOIN s1 ON {join_cond}"
	sql = f"{with_clause} {base}".strip()
	for t in dq.transforms or []:
		if getattr(t, "op", None) == "rolling_mean" and t.field and t.window and t.as_:
			alias = t.as_
			field = t.field
			window = int(t.window)
			sql = f"SELECT t.*, AVG({field}) OVER (PARTITION BY COALESCE(region,'') ORDER BY date ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW) AS {alias} FROM ({sql}) t"
	limit = dq.limit_points or 50000
	sql = f"{sql} LIMIT {limit}"
	return sql, params
