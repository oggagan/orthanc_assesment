"""HTTP exception handlers and standard error response schema."""

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dicom_middleware.observability.logging import correlation_id_ctx


class ErrorResponse(BaseModel):
    """RFC 7807-style error payload; all 4xx/5xx return this shape."""

    type: str | None = Field(default=None, description="URI or code identifying the error type")
    title: str = Field(description="Short summary")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Human-readable detail")
    correlation_id: str | None = Field(default=None, description="Request correlation ID for tracing")
    timestamp: str = Field(description="ISO 8601 timestamp")
    errors: list[dict[str, Any]] | None = Field(default=None, description="Validation or field errors")


def get_correlation_id() -> str | None:
    """Return current request correlation ID from context."""
    try:
        return correlation_id_ctx.get()
    except LookupError:
        return None


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle 422 validation errors with standard error body."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            type="validation_error",
            title="Validation Error",
            status=422,
            detail=exc.errors()[0].get("msg", "Request validation failed") if exc.errors() else "Validation failed",
            correlation_id=get_correlation_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            errors=exc.errors(),
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions with 500 and standard error body."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            type="internal_error",
            title="Internal Server Error",
            status=500,
            detail=str(exc) or "An unexpected error occurred",
            correlation_id=get_correlation_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            errors=None,
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for consistent error responses."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
