"""Aggregates v1 routes under /api/v1."""

from fastapi import APIRouter

from dicom_middleware.api.v1.routes import ingestion

api_router = APIRouter()
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["Ingestion"])
