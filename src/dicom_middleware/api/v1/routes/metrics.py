"""Prometheus metrics endpoint."""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=["Metrics"])


@router.get(
    "",
    summary="Prometheus metrics (text format)",
    description=(
        "Prometheus scrape endpoint. Returns `text/plain; charset=utf-8` in Prometheus exposition format. "
        "Used by Prometheus or compatible scrapers. Exposes pipeline, request, storage, and DLQ metrics."
    ),
)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
