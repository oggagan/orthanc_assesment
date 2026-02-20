"""OpenAPI tags, descriptions, shared response schemas, and metadata."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "**Liveness** (`/health`) indicates the process is running. **Readiness** (`/ready`) indicates the service is ready to accept traffic (currently always 200; DB/Kafka checks can be added later). Both return `{\"status\": \"ok\"}`.",
    },
    {
        "name": "Metrics",
        "description": "Prometheus scrape endpoint at `/metrics`. Returns `text/plain` in Prometheus exposition format. Used by Prometheus or compatible monitoring systems to collect pipeline, request, storage, and DLQ metrics.",
    },
    {
        "name": "Ingestion",
        "description": "Receive Orthanc study notifications via `POST /api/v1/ingestion/studies`. Triggers the full pipeline: fetch DICOM from Orthanc, extract metadata, upsert to DB, save raw DICOM (local or GCS), publish to Kafka. Request body includes Orthanc study `ID` and optional `Path`. Response includes `correlation_id` for tracing.",
    },
]


class HealthResponse(BaseModel):
    """Probe success payload."""

    status: Literal["ok"] = Field(description="Always 'ok' when the probe succeeds.")


class IngestionSuccessResponse(BaseModel):
    """Study accepted for processing."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": "accepted", "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
        }
    )

    status: Literal["accepted"] = Field(description="Indicates the study was accepted for processing.")
    correlation_id: str = Field(description="Request correlation ID for tracing.")


def custom_openapi_schema(app):
    """Add tags, servers, and ensure consistent API docs."""
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    servers = getattr(app, "servers", None) or [{"url": "http://localhost:8000", "description": "Local development"}]
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=OPENAPI_TAGS,
        servers=servers,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
