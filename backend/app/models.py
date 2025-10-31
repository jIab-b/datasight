from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Literal


class Source(BaseModel):
	dataset: str
	select: List[str]
	where: Optional[Dict[str, Union[str, int, float, List[Union[str, int, float]]]]] = None
	time: Optional[Dict[str, str]] = None


class Transform(BaseModel):
	op: Literal["rolling_mean", "fill_null", "pct_change", "resample", "alias", "calc"]
	field: Optional[str] = None
	window: Optional[int] = None
	grain: Optional[str] = None
	expr: Optional[str] = None
	as_: Optional[str] = Field(default=None, alias="as")


class DataQuery(BaseModel):
	sources: List[Source]
	join: Optional[Dict[str, Union[List[str], str]]] = None
	transforms: List[Transform] = Field(default_factory=list)
	limit_points: Optional[int] = 50000
	timezone: Optional[str] = "UTC"
	units: Optional[Dict[str, str]] = None

	model_config = {"populate_by_name": True}


class Channel(BaseModel):
	field: str
	type: Literal["quantitative", "temporal", "nominal", "ordinal"]
	axis: Optional[Literal["left", "right", "bottom", "top"]] = None


class ChartSpec(BaseModel):
	mark: Literal["line", "bar", "area", "scatter", "choropleth"]
	encoding: Dict[str, Union[Channel, List[Channel]]]
	title: Optional[str] = None
	interactions: List[Literal["tooltip", "brushX", "zoom", "legendFilter"]] = []


class PreviewResponse(BaseModel):
	sql: str
	rows: List[Dict[str, Union[str, int, float, None]]]


class RunResponse(BaseModel):
	receipt_id: str
	sql: str
	rows: List[Dict[str, Union[str, int, float, None]]]
