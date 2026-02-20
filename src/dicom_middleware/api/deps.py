"""Common dependencies for API routes."""

from dicom_middleware.observability.logging import correlation_id_ctx


def get_correlation_id() -> str | None:
    """Return current request correlation ID (set by middleware)."""
    try:
        return correlation_id_ctx.get()
    except LookupError:
        return None
