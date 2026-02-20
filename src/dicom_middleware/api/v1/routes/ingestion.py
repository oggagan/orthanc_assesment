"""Ingestion API - Orthanc webhook receiver."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from sqlalchemy.ext.asyncio import AsyncSession

from dicom_middleware.api.deps import get_correlation_id
from dicom_middleware.api.errors import ErrorResponse
from dicom_middleware.api.openapi import IngestionSuccessResponse
from dicom_middleware.application.use_cases import process_new_study
from dicom_middleware.db.session import get_db
from dicom_middleware.observability.logging import get_logger

_log = get_logger(__name__)

router = APIRouter()


class IngestionRequest(BaseModel):
    """Orthanc webhook payload: at least the study ID (Orthanc internal ID)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"ID": "abc-123-orthanc-id", "Path": "Study"},
        }
    )

    ID: str = Field(description="Orthanc study ID (internal identifier)")
    Path: str | None = Field(default=None, description="e.g. Study")


@router.post(
    "/studies",
    summary="Receive new study notification",
    description=(
        "Accepts an Orthanc study notification (e.g. from Orthanc webhook or manual call). "
        "Uses the Orthanc study ID to fetch the study, then runs the full pipeline: extract metadata, "
        "upsert to DB, save raw DICOM (local or GCS), and publish to Kafka. "
        "The correlation ID is set by middleware and returned for tracing. "
        "Idempotent: processing the same study again updates the DB row and produces a single Kafka event."
    ),
    response_model=IngestionSuccessResponse,
    responses={
        200: {"description": "Study accepted for processing", "model": IngestionSuccessResponse},
        422: {"description": "Validation error (e.g. missing or invalid body)", "model": ErrorResponse},
        502: {"description": "Pipeline failed (e.g. Orthanc unreachable, storage or Kafka error)", "model": ErrorResponse},
        500: {"description": "Internal error (e.g. missing correlation ID)", "model": ErrorResponse},
    },
)
async def ingest_study(
    body: IngestionRequest,
    session: AsyncSession = Depends(get_db),
) -> IngestionSuccessResponse:
    """Accept Orthanc study notification and run pipeline. Correlation ID is set by middleware."""
    correlation_id = get_correlation_id()
    if not correlation_id:
        raise HTTPException(status_code=500, detail="Missing correlation ID")
    try:
        await process_new_study(correlation_id, body.ID, session)
        return IngestionSuccessResponse(status="accepted", correlation_id=correlation_id)
    except Exception as e:
        _log.exception("ingestion_failed", correlation_id=correlation_id, error=str(e))
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {e}") from e
