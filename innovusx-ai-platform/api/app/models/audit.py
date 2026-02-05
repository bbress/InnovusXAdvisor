"""Audit and compliance data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Strategy operations
    STRATEGY_REQUEST = "strategy_request"
    STRATEGY_RESPONSE = "strategy_response"

    # Data operations
    DATA_ACCESS = "data_access"
    DATA_RETRIEVAL = "data_retrieval"

    # Model operations
    MODEL_INFERENCE = "model_inference"
    MODEL_FALLBACK = "model_fallback"

    # Security operations
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Governance operations
    PII_DETECTED = "pii_detected"
    PII_REDACTED = "pii_redacted"
    COMPLIANCE_CHECK = "compliance_check"
    BIAS_CHECK = "bias_check"

    # Admin operations
    CONFIG_CHANGE = "config_change"
    MODEL_DEPLOYMENT = "model_deployment"


class ComplianceStatus(str, Enum):
    """Compliance check status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class PIIEntity(BaseModel):
    """Detected PII entity."""
    entity_type: str
    start_position: int
    end_position: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    action_taken: str  # detected, redacted, blocked


class ComplianceCheck(BaseModel):
    """Result of a compliance check."""
    check_name: str
    status: ComplianceStatus
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditEntry(BaseModel):
    """Immutable audit log entry."""
    # Identification
    id: str = Field(..., description="Unique audit entry ID")
    correlation_id: str = Field(..., description="Request correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Action details
    action: AuditAction
    resource: str = Field(..., description="Resource being accessed")
    operation: str = Field(..., description="Specific operation performed")

    # Actor information
    user_id: Optional[str] = None
    api_key_id: Optional[str] = None
    ip_address: str
    user_agent: str

    # Request/Response hashes (for integrity)
    input_hash: str = Field(..., description="SHA-256 of input")
    output_hash: Optional[str] = Field(None, description="SHA-256 of output")

    # Context
    model_version: Optional[str] = None
    parameters: dict = Field(default_factory=dict)

    # Results
    status: str  # success, failure, blocked
    error_message: Optional[str] = None
    latency_ms: int

    # Compliance
    pii_detected: bool = False
    pii_entities: list[PIIEntity] = Field(default_factory=list)
    compliance_checks: list[ComplianceCheck] = Field(default_factory=list)

    # Chain hash for tamper detection
    previous_hash: Optional[str] = None
    chain_hash: Optional[str] = None

    class Config:
        frozen = True  # Make immutable


class AuditQuery(BaseModel):
    """Query parameters for audit log search."""
    correlation_id: Optional[str] = None
    action: Optional[AuditAction] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditSummary(BaseModel):
    """Summary statistics for audit logs."""
    total_entries: int
    period_start: datetime
    period_end: datetime

    # Action breakdown
    actions_by_type: dict[str, int]

    # Status breakdown
    success_count: int
    failure_count: int
    blocked_count: int

    # Compliance summary
    pii_detections: int
    compliance_failures: int

    # Performance summary
    avg_latency_ms: float
    p99_latency_ms: float


class AuditTrailEntry(BaseModel):
    """Simplified audit entry for trail visualization."""
    timestamp: datetime
    action: AuditAction
    status: str
    details: str
    latency_ms: int


class AuditTrail(BaseModel):
    """Complete audit trail for a request."""
    correlation_id: str
    entries: list[AuditTrailEntry]
    total_latency_ms: int
    compliance_status: ComplianceStatus
    pii_detected: bool


class GovernanceMetrics(BaseModel):
    """Governance and compliance metrics."""
    # Audit coverage
    audit_coverage_percent: float = Field(..., ge=0.0, le=100.0)

    # PII handling
    pii_detections_today: int
    pii_incidents_today: int = 0

    # Bias monitoring
    bias_score: float = Field(..., ge=0.0, le=1.0)
    bias_threshold: float = Field(default=0.1)
    bias_status: ComplianceStatus

    # Access control
    auth_failures_today: int
    rate_limit_violations_today: int

    # Overall status
    overall_status: ComplianceStatus
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class GovernanceControl(BaseModel):
    """Individual governance control status."""
    name: str
    description: str
    enabled: bool
    status: ComplianceStatus
    last_check: datetime
    details: Optional[dict] = None


class GovernanceReport(BaseModel):
    """Complete governance status report."""
    controls: list[GovernanceControl]
    metrics: GovernanceMetrics
    generated_at: datetime = Field(default_factory=datetime.utcnow)
