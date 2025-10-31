from fastapi import APIRouter
from ..db import fetch_all, fetch_one

router = APIRouter()


@router.get("/datasets")
def list_datasets(q: str | None = None):
	if q:
		return fetch_all(
			"SELECT id, name, topic FROM datasets WHERE name ILIKE %(q)s OR id ILIKE %(q)s ORDER BY name LIMIT 100",
			{"q": f"%{q}%"},
		)
	return fetch_all("SELECT id, name, topic FROM datasets ORDER BY name LIMIT 100", {})


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
	ds = fetch_one(
		"SELECT id, name, publisher, license, topic, description, source_url, update_cadence FROM datasets WHERE id=%(id)s",
		{"id": dataset_id},
	)
	if not ds:
		return {"error": "not_found"}
	fields = fetch_all(
		"SELECT name, dtype, unit, semantic_role, description FROM fields WHERE dataset_id=%(id)s",
		{"id": dataset_id},
	)
	ds["fields"] = fields
	return ds
