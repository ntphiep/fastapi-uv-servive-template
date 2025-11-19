import uuid
from contextlib import asynccontextmanager

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from python_service_template.api.health import router as health_router
from python_service_template.api.v1.coffee import router as coffee_router
from python_service_template.dependencies import settings
from python_service_template.settings import configure_structlog, create_std_logging_config

# Centralized settings initialization
_app_settings = settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure structlog for each worker process
    configure_structlog(_app_settings.app_version, _app_settings.git_commit_sha, _app_settings.logging)
    app.state.instrumentator.expose(app, include_in_schema=False)
    app.state.log = structlog.get_logger("app")
    await app.state.log.awarning("Starting application")
    yield
    await app.state.log.awarning("Shutting down application")


app = FastAPI(
    title="Python Service Template",
    description="Batteries-included starter template for Python backend services",
    version=_app_settings.app_version,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
    validator=None,
)
app.include_router(coffee_router)
app.include_router(health_router)
instrumentator = Instrumentator().instrument(app)
app.state.instrumentator = instrumentator


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
    await app.state.log.aexception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


if __name__ == "__main__":
    import argparse
    import asyncio

    import uvicorn
    import uvloop

    parser = argparse.ArgumentParser(description="Run the FastAPI service.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development.",
    )
    args = parser.parse_args()

    # Configure uvloop as the event loop policy
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    workers = None if args.reload else _app_settings.workers
    uvicorn.run(
        f"{__name__}:app",
        host=_app_settings.host,
        port=_app_settings.port,
        log_config=create_std_logging_config(
            _app_settings.app_version, _app_settings.git_commit_sha, _app_settings.logging
        ),
        access_log=True,
        reload=args.reload,
        workers=workers,
    )
