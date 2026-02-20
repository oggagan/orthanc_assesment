"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from dicom_middleware.api.errors import register_exception_handlers
from dicom_middleware.api.v1.router import api_router
from dicom_middleware.api.v1.routes.health import router as health_router
from dicom_middleware.api.v1.routes.metrics import router as metrics_router
from dicom_middleware.config import get_settings
from dicom_middleware.api.openapi import OPENAPI_TAGS, custom_openapi_schema
from dicom_middleware.correlation import CorrelationIdMiddleware
from dicom_middleware.observability.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    settings = get_settings()
    configure_logging(settings.log_level)
    from dicom_middleware.application.orthanc_poller import run_orthanc_poller
    from dicom_middleware.db.session import init_db
    await init_db()
    poller_task = asyncio.create_task(run_orthanc_poller())
    yield
    poller_task.cancel()
    try:
        await poller_task
    except asyncio.CancelledError:
        pass
    from dicom_middleware.infrastructure.kafka_producer import close_producer
    from dicom_middleware.infrastructure.dlq import close_dlq_producer
    await close_producer()
    await close_dlq_producer()


APP_DESCRIPTION = """
DICOM Middleware ingests DICOM studies from Orthanc, persists metadata to PostgreSQL, stores raw DICOM (locally or in Google Cloud Storage), and publishes events to Kafka.

**Pipeline:** On ingestion (e.g. Orthanc webhook or manual POST), the service fetches the study from Orthanc, extracts metadata (Study Instance UID, Patient ID, Modality, Study Date), upserts into the canonical `studies` table, saves the raw DICOM to the configured storage backend (local filesystem or GCS), and publishes a metadata event to the `dicom.metadata.v1` Kafka topic. Failures are sent to a dead-letter topic.

**Storage:** Raw DICOM can be stored on local disk (`STORAGE_BACKEND=local`) or in a GCS bucket (`STORAGE_BACKEND=gcs`). The Kafka event includes the storage path or URI (`file://` or `gs://`) for downstream consumers.

**API:** Versioned under `/api/v1`. Health and metrics are at `/health`, `/ready`, and `/metrics`.
"""


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="DICOM Middleware POC",
        description=APP_DESCRIPTION.strip(),
        version="0.1.0",
        servers=[{"url": "http://localhost:8000", "description": "Local development"}],
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.openapi = lambda: custom_openapi_schema(app)
    app.add_middleware(CorrelationIdMiddleware)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(metrics_router, prefix="/metrics")
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
