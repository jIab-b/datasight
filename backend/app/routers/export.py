from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from ..db import fetch_one, connection

router = APIRouter()


def _csv_stream(sql: str):
	def gen():
		with connection() as conn:
			cur = conn.cursor()
			cur.execute(sql)
			headers = [d[0] for d in cur.description]
			yield ",".join(headers) + "\n"
			for r in cur:
				yield ",".join(["" if x is None else str(x) for x in r]) + "\n"
	return gen()


@router.get("/csv")
def export_csv(receipt: str):
	rec = fetch_one("SELECT sql FROM query_receipts WHERE id=:id", {"id": receipt})
	if not rec:
		return Response(status_code=404)
	return StreamingResponse(_csv_stream(rec["sql"]), media_type="text/csv")
