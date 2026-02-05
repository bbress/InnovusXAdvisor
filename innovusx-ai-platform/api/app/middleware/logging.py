"""Structured logging configuration."""

import sys
import uuid
from typing import Optional

import structlog
from fastapi import Request


def setup_logging(json_logs: bool = True, log_level: str = "INFO") -> None:
    """Configure structured logging with structlog."""

    # Shared processors for all loggers
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # JSON output for production
        shared_processors.append(structlog.processors.format_exc_info)
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty output for development
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_correlation_id(request: Request) -> str:
    """Extract or generate correlation ID from request."""
    # Check for existing correlation ID in headers
    correlation_id = request.headers.get("X-Correlation-ID")

    if not correlation_id:
        # Check for request ID
        correlation_id = request.headers.get("X-Request-ID")

    if not correlation_id:
        # Generate new correlation ID
        correlation_id = f"req-{uuid.uuid4().hex[:12]}"

    return correlation_id


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers (when behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get first IP in chain
        return forwarded_for.split(",")[0].strip()

    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct client
    if request.client:
        return request.client.host

    return "unknown"


class LogContext:
    """Context manager for structured logging with automatic cleanup."""

    def __init__(self, **kwargs):
        self.context = kwargs
        self._token = None

    def __enter__(self):
        self._token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_with_context(
    logger: structlog.BoundLogger,
    level: str,
    message: str,
    correlation_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log a message with optional context."""
    log_method = getattr(logger, level.lower(), logger.info)

    if correlation_id:
        kwargs["correlation_id"] = correlation_id

    log_method(message, **kwargs)
