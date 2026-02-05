"""Audit and governance API endpoints."""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, Query, HTTPException, status

from app.models.audit import (
    AuditEntry,
    AuditAction,
    AuditQuery,
    AuditSummary,
    AuditTrail,
    AuditTrailEntry,
    ComplianceStatus,
    ComplianceCheck,
    PIIEntity,
    GovernanceMetrics,
    GovernanceControl,
    GovernanceReport,
)

router = APIRouter(prefix="/audit")


@router.get(
    "/trail/{correlation_id}",
    response_model=AuditTrail,
    summary="Get audit trail",
    description="Returns the complete audit trail for a specific request"
)
async def get_audit_trail(correlation_id: str) -> AuditTrail:
    """
    Get the complete audit trail for a request.

    Shows all operations performed during request processing,
    useful for debugging and compliance verification.
    """
    # In production, this would query the audit log database
    # For demo, return mock data
    entries = [
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(seconds=2, milliseconds=234),
            action=AuditAction.STRATEGY_REQUEST,
            status="success",
            details="Request received and validated",
            latency_ms=10
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(seconds=2, milliseconds=200),
            action=AuditAction.PII_DETECTED,
            status="success",
            details="PII scan completed: No sensitive data found",
            latency_ms=34
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(seconds=2, milliseconds=150),
            action=AuditAction.DATA_RETRIEVAL,
            status="success",
            details="Retrieved 12 relevant documents from knowledge base",
            latency_ms=85
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(seconds=1, milliseconds=800),
            action=AuditAction.MODEL_INFERENCE,
            status="success",
            details="GPT-4 Turbo inference completed (856 tokens)",
            latency_ms=1150
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(milliseconds=600),
            action=AuditAction.COMPLIANCE_CHECK,
            status="success",
            details="Output validation passed all safety checks",
            latency_ms=45
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(milliseconds=500),
            action=AuditAction.BIAS_CHECK,
            status="success",
            details="Bias score: 0.02 (threshold: 0.10)",
            latency_ms=30
        ),
        AuditTrailEntry(
            timestamp=datetime.utcnow() - timedelta(milliseconds=450),
            action=AuditAction.STRATEGY_RESPONSE,
            status="success",
            details="Response delivered successfully",
            latency_ms=5
        ),
    ]

    total_latency = sum(e.latency_ms for e in entries)

    return AuditTrail(
        correlation_id=correlation_id,
        entries=entries,
        total_latency_ms=total_latency,
        compliance_status=ComplianceStatus.PASSED,
        pii_detected=False
    )


@router.get(
    "/summary",
    response_model=AuditSummary,
    summary="Get audit summary",
    description="Returns summary statistics for audit logs"
)
async def get_audit_summary(
    hours: int = Query(default=24, ge=1, le=720, description="Hours to summarize")
) -> AuditSummary:
    """
    Get summary statistics for audit logs.

    Provides aggregated metrics for a specified time period.
    """
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(hours=hours)

    # In production, this would aggregate from the audit database
    return AuditSummary(
        total_entries=12450,
        period_start=period_start,
        period_end=period_end,
        actions_by_type={
            "strategy_request": 2100,
            "strategy_response": 2095,
            "data_retrieval": 2100,
            "model_inference": 2100,
            "compliance_check": 2100,
            "pii_detected": 45,
            "pii_redacted": 12,
            "auth_success": 1890,
            "rate_limit_exceeded": 5
        },
        success_count=12400,
        failure_count=45,
        blocked_count=5,
        pii_detections=45,
        compliance_failures=0,
        avg_latency_ms=1250.5,
        p99_latency_ms=2850.0
    )


@router.get(
    "/governance",
    response_model=GovernanceReport,
    summary="Get governance report",
    description="Returns complete governance and compliance status"
)
async def get_governance_report() -> GovernanceReport:
    """
    Get comprehensive governance and compliance report.

    Includes:
    - All governance controls and their status
    - Compliance metrics
    - PII handling statistics
    - Bias monitoring results
    """
    controls = [
        GovernanceControl(
            name="Audit Logging",
            description="Complete audit trail for all requests",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(minutes=1),
            details={"coverage": "100%", "retention_days": 90}
        ),
        GovernanceControl(
            name="PII Detection",
            description="Automatic detection and redaction of personal information",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(minutes=1),
            details={"engine": "Presidio", "entities_supported": 8}
        ),
        GovernanceControl(
            name="Access Control",
            description="Role-based access control for API endpoints",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(minutes=5),
            details={"roles_defined": 4, "active_api_keys": 12}
        ),
        GovernanceControl(
            name="Rate Limiting",
            description="Request rate limiting to prevent abuse",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow(),
            details={"per_minute": 60, "per_hour": 500}
        ),
        GovernanceControl(
            name="Bias Monitoring",
            description="Continuous monitoring for output bias",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(hours=1),
            details={"threshold": 0.10, "current_score": 0.02}
        ),
        GovernanceControl(
            name="Output Validation",
            description="Safety checks on all generated content",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(minutes=1),
            details={"checks": ["harmful_content", "pii_leakage", "prompt_injection"]}
        ),
        GovernanceControl(
            name="Model Versioning",
            description="Version control and rollback capability for models",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(hours=6),
            details={"current_version": "v2.3", "versions_available": 5}
        ),
        GovernanceControl(
            name="Data Encryption",
            description="Encryption at rest and in transit",
            enabled=True,
            status=ComplianceStatus.PASSED,
            last_check=datetime.utcnow() - timedelta(days=1),
            details={"at_rest": "AES-256", "in_transit": "TLS 1.3"}
        ),
    ]

    metrics = GovernanceMetrics(
        audit_coverage_percent=100.0,
        pii_detections_today=45,
        pii_incidents_today=0,
        bias_score=0.02,
        bias_threshold=0.10,
        bias_status=ComplianceStatus.PASSED,
        auth_failures_today=12,
        rate_limit_violations_today=5,
        overall_status=ComplianceStatus.PASSED
    )

    return GovernanceReport(
        controls=controls,
        metrics=metrics
    )


@router.get(
    "/entries",
    response_model=list[AuditEntry],
    summary="Query audit entries",
    description="Search and filter audit log entries"
)
async def query_audit_entries(
    action: Optional[AuditAction] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
) -> list[AuditEntry]:
    """
    Query audit log entries with filtering.

    Supports filtering by action type, status, and time range.
    """
    # In production, this would query the audit database with filters
    # For demo, return a sample entry
    sample_entry = AuditEntry(
        id=f"audit-{uuid.uuid4().hex[:12]}",
        correlation_id=f"req-{uuid.uuid4().hex[:12]}",
        timestamp=datetime.utcnow() - timedelta(minutes=5),
        action=action or AuditAction.STRATEGY_REQUEST,
        resource="/api/v1/strategy/generate",
        operation="POST",
        user_id=None,
        api_key_id="key_demo_001",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        input_hash="sha256:abc123...",
        output_hash="sha256:def456...",
        model_version="v2.3",
        parameters={"industry": "fintech", "company_stage": "growth"},
        status=status or "success",
        error_message=None,
        latency_ms=1250,
        pii_detected=False,
        pii_entities=[],
        compliance_checks=[
            ComplianceCheck(
                check_name="pii_scan",
                status=ComplianceStatus.PASSED,
                details="No PII detected"
            ),
            ComplianceCheck(
                check_name="output_safety",
                status=ComplianceStatus.PASSED,
                details="All safety checks passed"
            )
        ]
    )

    return [sample_entry]
