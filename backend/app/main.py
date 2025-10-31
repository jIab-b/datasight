from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from .db import init_pool
from .routers import catalog, query, charts, export
import os


def create_app() -> FastAPI:
	app = FastAPI(title="datasight", default_response_class=ORJSONResponse)
	origins = [os.getenv("FRONTEND_ORIGIN", "*")]
	app.add_middleware(
		CORSMiddleware,
		allow_origins=origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	@app.on_event("startup")
	def _startup() -> None:
		init_pool()

	app.include_router(catalog.router, prefix="/api/catalog", tags=["catalog"])
	app.include_router(query.router, prefix="/api/query", tags=["query"])
	app.include_router(charts.router, prefix="/api/charts", tags=["charts"])
	app.include_router(export.router, prefix="/api/export", tags=["export"])
	return app


app = create_app()
