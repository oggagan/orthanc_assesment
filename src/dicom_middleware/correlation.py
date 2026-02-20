"""Correlation ID middleware and context."""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from dicom_middleware.observability.logging import correlation_id_ctx

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Generate or propagate correlation ID and set in context for the request."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        correlation_id_ctx.set(correlation_id)
        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
