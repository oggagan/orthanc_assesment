"""Health and readiness endpoints (mounted at root: /health, /ready)."""

from fastapi import APIRouter

from dicom_middleware.api.openapi import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Liveness probe",
    description="Returns 200 if the application process is running. Use for Kubernetes liveness probes.",
    response_model=HealthResponse,
    responses={200: {"description": "Service is alive", "model": HealthResponse}},
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns 200 if the service is ready to accept traffic. DB/Kafka checks can be added later.",
    response_model=HealthResponse,
    responses={200: {"description": "Service is ready to accept traffic", "model": HealthResponse}},
)
async def ready() -> HealthResponse:
    return HealthResponse(status="ok")
