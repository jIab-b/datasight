from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from .db import init_pool
from .routers import catalog, query, charts, export
import os
import sys


def create_app() -> FastAPI:
	app = FastAPI(title="datasight", default_response_class=ORJSONResponse)

	# CORS: Allow localhost on any port for development
	app.add_middleware(
		CORSMiddleware,
		allow_origin_regex=r"http://(?:localhost|127\.0\.0\.1)(?::\d+)?",
		allow_credentials=False,
		allow_methods=["*"],
		allow_headers=["*"],
	)

	@app.exception_handler(RequestValidationError)
	async def validation_exception_handler(request: Request, exc: RequestValidationError):
		print(f"[ERROR] Validation error: {exc}", file=sys.stderr)
		return ORJSONResponse(
			status_code=422,
			content={"error": str(exc), "detail": exc.errors()}
		)

	@app.exception_handler(Exception)
	async def general_exception_handler(request: Request, exc: Exception):
		print(f"[ERROR] Unhandled exception: {type(exc).__name__}: {exc}", file=sys.stderr)
		import traceback
		traceback.print_exc(file=sys.stderr)
		return ORJSONResponse(
			status_code=500,
			content={"error": str(exc)}
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
