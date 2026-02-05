"""Telemetry and monitoring data models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class PipelineStage(str, Enum):
    """ML pipeline stages."""
    DATA_INGESTION = "data_ingestion"
    DATA_VALIDATION = "data_validation"
    EMBEDDING_GENERATION = "embedding_generation"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_DEPLOYMENT = "model_deployment"


class PipelineStageStatus(BaseModel):
    """Status of a single pipeline stage."""
    stage: PipelineStage
    status: HealthStatus
    last_run: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None


class PipelineStatus(BaseModel):
    """Overall ML pipeline status."""
    stages: list[PipelineStageStatus]
    last_successful_run: Optional[datetime] = None
    next_scheduled_run: Optional[datetime] = None
    overall_status: HealthStatus

    @classmethod
    def compute_overall_status(cls, stages: list[PipelineStageStatus]) -> HealthStatus:
        """Compute overall status from stage statuses."""
        statuses = [s.status for s in stages]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED


class ModelVersion(BaseModel):
    """Model version information."""
    version: str
    deployed_at: datetime
    is_active: bool
    performance_score: float = Field(..., ge=0.0, le=1.0)
    requests_served: int = Field(default=0, ge=0)


class ModelMetrics(BaseModel):
    """Current model performance metrics."""
    model_name: str
    current_version: str
    versions: list[ModelVersion]

    # Performance metrics
    avg_latency_ms: float
    p50_latency_ms: float
    p99_latency_ms: float
    requests_per_minute: float
    error_rate: float = Field(..., ge=0.0, le=1.0)

    # Quality metrics
    avg_quality_score: float = Field(..., ge=0.0, le=1.0)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    groundedness_score: float = Field(..., ge=0.0, le=1.0)

    # Resource usage
    tokens_used_today: int
    cost_today_usd: float
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0)


class DriftType(str, Enum):
    """Types of drift detection."""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    EMBEDDING_DRIFT = "embedding_drift"
    PREDICTION_DRIFT = "prediction_drift"


class DriftMetrics(BaseModel):
    """Drift detection metrics."""
    drift_type: DriftType
    drift_score: float = Field(..., ge=0.0, le=1.0)
    threshold: float = Field(..., ge=0.0, le=1.0)
    is_drifting: bool
    last_checked: datetime
    reference_period: str
    comparison_period: str
    details: Optional[dict] = None

    @property
    def status(self) -> HealthStatus:
        """Get health status based on drift."""
        if not self.is_drifting:
            return HealthStatus.HEALTHY
        elif self.drift_score < self.threshold * 1.5:
            return HealthStatus.DEGRADED
        return HealthStatus.UNHEALTHY


class DriftReport(BaseModel):
    """Complete drift detection report."""
    metrics: list[DriftMetrics]
    overall_status: HealthStatus
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    recommendations: list[str] = Field(default_factory=list)


class ComponentHealth(BaseModel):
    """Health status of a system component."""
    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[dict] = None


class SystemHealth(BaseModel):
    """Overall system health status."""
    status: HealthStatus
    components: list[ComponentHealth]
    uptime_seconds: float
    version: str
    environment: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def compute_overall_status(cls, components: list[ComponentHealth]) -> HealthStatus:
        """Compute overall status from component health."""
        statuses = [c.status for c in components]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED


class ArchitectureComponent(BaseModel):
    """Architecture component for visualization."""
    id: str
    name: str
    type: str
    status: HealthStatus
    metrics: dict = Field(default_factory=dict)
    connections: list[str] = Field(default_factory=list)


class ArchitectureView(BaseModel):
    """Architecture visualization data."""
    components: list[ArchitectureComponent]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
