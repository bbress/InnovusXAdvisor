"""FastAPI application entry point."""

import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.config import settings
from app.routers import strategy, telemetry, audit, health
from app.middleware.logging import setup_logging, get_correlation_id
from app.middleware.rate_limit import RateLimitMiddleware

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )

    # Initialize database connection pool
    # await init_database()

    # Initialize Redis connection
    # await init_redis()

    # Load knowledge base into vector store
    # await init_vector_store()

    yield

    # Shutdown
    logger.info("Shutting down application")
    # await close_database()
    # await close_redis()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI platform for business strategy generation",
    version=settings.app_version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_requests_per_minute
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests with correlation ID and timing."""
    correlation_id = get_correlation_id(request)
    start_time = time.perf_counter()

    # Add correlation ID to request state
    request.state.correlation_id = correlation_id

    # Process request
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)

        # Log request
        logger.info(
            "Request completed",
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=round(process_time * 1000, 2)
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as exc:
        process_time = time.perf_counter() - start_time
        logger.error(
            "Request failed",
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            error=str(exc),
            latency_ms=round(process_time * 1000, 2)
        )
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    logger.error(
        "Unhandled exception",
        correlation_id=correlation_id,
        error=str(exc),
        error_type=type(exc).__name__
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "detail": str(exc) if settings.is_development else None
        }
    )


# Include routers
app.include_router(
    health.router,
    tags=["Health"]
)

app.include_router(
    strategy.router,
    prefix=settings.api_prefix,
    tags=["Strategy"]
)

app.include_router(
    telemetry.router,
    prefix=settings.api_prefix,
    tags=["Telemetry"]
)

app.include_router(
    audit.router,
    prefix=settings.api_prefix,
    tags=["Audit"]
)


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs" if settings.is_development else None,
        "api": settings.api_prefix
    }
