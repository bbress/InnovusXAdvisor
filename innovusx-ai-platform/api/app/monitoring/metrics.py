"""Metrics collection for monitoring and observability."""

import time
from functools import lru_cache
from typing import Optional

import structlog
from prometheus_client import Counter, Histogram, Gauge, Info

from app.config import settings

logger = structlog.get_logger()


# Request metrics
REQUESTS_TOTAL = Counter(
    "innovusx_requests_total",
    "Total number of requests",
    ["endpoint", "method", "status"]
)

REQUEST_LATENCY = Histogram(
    "innovusx_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Strategy generation metrics
STRATEGIES_GENERATED = Counter(
    "innovusx_strategies_generated_total",
    "Total number of strategies generated",
    ["industry", "focus_area"]
)

STRATEGY_QUALITY = Histogram(
    "innovusx_strategy_quality_score",
    "Quality scores of generated strategies",
    ["metric"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# LLM metrics
LLM_REQUESTS = Counter(
    "innovusx_llm_requests_total",
    "Total LLM API requests",
    ["provider", "model", "status"]
)

LLM_LATENCY = Histogram(
    "innovusx_llm_latency_seconds",
    "LLM inference latency",
    ["provider", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

LLM_TOKENS = Counter(
    "innovusx_llm_tokens_total",
    "Total tokens used",
    ["provider", "model", "type"]
)

LLM_COST = Counter(
    "innovusx_llm_cost_usd_total",
    "Total LLM costs in USD",
    ["provider", "model"]
)

# RAG metrics
RAG_RETRIEVALS = Counter(
    "innovusx_rag_retrievals_total",
    "Total RAG retrievals",
    ["status"]
)

RAG_LATENCY = Histogram(
    "innovusx_rag_latency_seconds",
    "RAG retrieval latency",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

RAG_DOCUMENTS = Histogram(
    "innovusx_rag_documents_retrieved",
    "Number of documents retrieved per query",
    buckets=[1, 2, 5, 10, 15, 20]
)

# Cache metrics
CACHE_HITS = Counter(
    "innovusx_cache_hits_total",
    "Total cache hits",
    ["cache_type"]
)

CACHE_MISSES = Counter(
    "innovusx_cache_misses_total",
    "Total cache misses",
    ["cache_type"]
)

# Governance metrics
PII_DETECTIONS = Counter(
    "innovusx_pii_detections_total",
    "Total PII detections",
    ["entity_type", "action"]
)

AUDIT_ENTRIES = Counter(
    "innovusx_audit_entries_total",
    "Total audit log entries",
    ["action", "status"]
)

# Drift metrics
DRIFT_SCORE = Gauge(
    "innovusx_drift_score",
    "Current drift score",
    ["drift_type"]
)

# System info
SYSTEM_INFO = Info(
    "innovusx_system",
    "System information"
)


class MetricsCollector:
    """
    Centralized metrics collection.

    Provides methods to record various metrics across the system.
    """

    def __init__(self):
        # Set system info
        SYSTEM_INFO.info({
            "version": settings.app_version,
            "environment": settings.environment,
            "primary_model": settings.llm_primary_model
        })

        logger.info("Metrics collector initialized")

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_seconds: float
    ):
        """Record HTTP request metrics."""
        REQUESTS_TOTAL.labels(
            endpoint=endpoint,
            method=method,
            status=str(status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            endpoint=endpoint,
            method=method
        ).observe(latency_seconds)

    def record_strategy_generation(
        self,
        industry: str,
        focus_area: Optional[str],
        quality_metrics: dict
    ):
        """Record strategy generation metrics."""
        STRATEGIES_GENERATED.labels(
            industry=industry,
            focus_area=focus_area or "none"
        ).inc()

        # Record quality scores
        for metric_name, score in quality_metrics.items():
            STRATEGY_QUALITY.labels(metric=metric_name).observe(score)

    def record_llm_request(
        self,
        provider: str,
        model: str,
        status: str,
        latency_seconds: float,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float
    ):
        """Record LLM request metrics."""
        LLM_REQUESTS.labels(
            provider=provider,
            model=model,
            status=status
        ).inc()

        LLM_LATENCY.labels(
            provider=provider,
            model=model
        ).observe(latency_seconds)

        LLM_TOKENS.labels(
            provider=provider,
            model=model,
            type="input"
        ).inc(tokens_input)

        LLM_TOKENS.labels(
            provider=provider,
            model=model,
            type="output"
        ).inc(tokens_output)

        LLM_COST.labels(
            provider=provider,
            model=model
        ).inc(cost_usd)

    def record_rag_retrieval(
        self,
        status: str,
        latency_seconds: float,
        documents_count: int
    ):
        """Record RAG retrieval metrics."""
        RAG_RETRIEVALS.labels(status=status).inc()
        RAG_LATENCY.observe(latency_seconds)
        RAG_DOCUMENTS.observe(documents_count)

    def record_cache_access(
        self,
        cache_type: str,
        hit: bool
    ):
        """Record cache access."""
        if hit:
            CACHE_HITS.labels(cache_type=cache_type).inc()
        else:
            CACHE_MISSES.labels(cache_type=cache_type).inc()

    def record_pii_detection(
        self,
        entity_type: str,
        action: str
    ):
        """Record PII detection event."""
        PII_DETECTIONS.labels(
            entity_type=entity_type,
            action=action
        ).inc()

    def record_audit_entry(
        self,
        action: str,
        status: str
    ):
        """Record audit log entry."""
        AUDIT_ENTRIES.labels(
            action=action,
            status=status
        ).inc()

    def update_drift_score(
        self,
        drift_type: str,
        score: float
    ):
        """Update drift score gauge."""
        DRIFT_SCORE.labels(drift_type=drift_type).set(score)


@lru_cache
def get_metrics_collector() -> MetricsCollector:
    """Get metrics collector instance."""
    return MetricsCollector()
