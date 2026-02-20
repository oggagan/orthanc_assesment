"""Structured JSON logging with correlation ID support."""

import logging
import sys
from contextvars import ContextVar

import structlog

# Correlation ID is set by middleware; observability uses this for every log line.
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def _add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict
) -> dict:
    """Inject correlation_id from context into every log event."""
    try:
        cid = correlation_id_ctx.get()
        if cid is not None:
            event_dict["correlation_id"] = cid
    except LookupError:
        pass
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog for JSON output and bind correlation_id from context."""
    structlog.configure(
        processors=[
            _add_correlation_id,
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(*args: str) -> structlog.BoundLogger:
    """Return a logger that will include correlation_id when bound."""
    return structlog.get_logger(*args)
