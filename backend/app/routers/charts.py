from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4
from ..db import execute, fetch_one
from ..models import ChartSpec

router = APIRouter()


class SaveRequest(BaseModel):
	receipt_id: str
	chartspec: ChartSpec
	title: str | None = None


@router.post("/save")
def save_chart(req: SaveRequest):
	chart_id = str(uuid4())
	execute(
		"INSERT INTO charts (id, receipt_id, chartspec, title) VALUES (:id, :rid, :cs, :title)",
		{"id": chart_id, "rid": req.receipt_id, "cs": req.chartspec.model_dump_json(), "title": req.title},
	)
	return {"id": chart_id}


@router.get("/{chart_id}")
def get_chart(chart_id: str):
	row = fetch_one(
		"SELECT id, receipt_id, chartspec, title, share_slug, created_at FROM charts WHERE id=:id",
		{"id": chart_id},
	)
	if not row:
		return {"error": "not_found"}
	return row
