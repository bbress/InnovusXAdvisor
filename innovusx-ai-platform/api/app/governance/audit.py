"""Audit logging system for compliance and traceability."""

import hashlib
import json
import time
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Optional, Any

import structlog
from pydantic import BaseModel

from app.config import settings
from app.models.strategy import StrategyRequest, StrategyResponse
from app.models.audit import (
    AuditEntry,
    AuditAction,
    ComplianceStatus,
    ComplianceCheck,
)

logger = structlog.get_logger()


class AuditLogger:
    """
    Comprehensive audit logging system.

    Features:
    - Immutable audit entries
    - Chain hashing for tamper detection
    - Structured logging for analysis
    - Compliance-ready format
    """

    def __init__(self):
        self._previous_hash: Optional[str] = None
        self._entries: list[AuditEntry] = []  # In production, use database

        logger.info("Audit logger initialized")

    def _hash_content(self, content: Any) -> str:
        """Create SHA-256 hash of content."""
        if isinstance(content, BaseModel):
            content = content.model_dump_json()
        elif not isinstance(content, str):
            content = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def _create_chain_hash(self, entry_data: dict) -> str:
        """Create chain hash linking to previous entry."""
        chain_content = f"{self._previous_hash}:{json.dumps(entry_data, sort_keys=True, default=str)}"
        return hashlib.sha256(chain_content.encode()).hexdigest()

    async def log(
        self,
        action: AuditAction,
        resource: str,
        operation: str,
        correlation_id: str,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        input_data: Any = None,
        output_data: Any = None,
        model_version: Optional[str] = None,
        parameters: Optional[dict] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        latency_ms: int = 0,
        pii_detected: bool = False,
        pii_entities: Optional[list] = None,
        compliance_checks: Optional[list[ComplianceCheck]] = None
    ) -> AuditEntry:
        """
        Create an immutable audit log entry.

        Args:
            action: Type of action being logged
            resource: Resource being accessed
            operation: Specific operation performed
            correlation_id: Request correlation ID
            ... (other parameters)

        Returns:
            AuditEntry: The created audit entry
        """
        entry_id = f"audit-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow()

        # Hash input and output
        input_hash = self._hash_content(input_data) if input_data else ""
        output_hash = self._hash_content(output_data) if output_data else None

        # Create entry data for chain hash
        entry_data = {
            "id": entry_id,
            "timestamp": timestamp.isoformat(),
            "action": action.value,
            "correlation_id": correlation_id,
            "input_hash": input_hash
        }

        # Create chain hash
        chain_hash = self._create_chain_hash(entry_data)

        # Create audit entry
        entry = AuditEntry(
            id=entry_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            action=action,
            resource=resource,
            operation=operation,
            user_id=user_id,
            api_key_id=api_key_id,
            ip_address=ip_address,
            user_agent=user_agent,
            input_hash=input_hash,
            output_hash=output_hash,
            model_version=model_version,
            parameters=parameters or {},
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
            pii_detected=pii_detected,
            pii_entities=pii_entities or [],
            compliance_checks=compliance_checks or [],
            previous_hash=self._previous_hash,
            chain_hash=chain_hash
        )

        # Update chain
        self._previous_hash = chain_hash

        # Store entry (in production, persist to database)
        self._entries.append(entry)

        # Also log to structured logger
        logger.info(
            "Audit entry created",
            audit_id=entry_id,
            action=action.value,
            correlation_id=correlation_id,
            status=status,
            latency_ms=latency_ms
        )

        return entry

    async def log_strategy_generation(
        self,
        correlation_id: str,
        request: StrategyRequest,
        response: Optional[StrategyResponse],
        pii_detected: bool,
        latency_ms: int,
        status: str,
        error_message: Optional[str] = None,
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> AuditEntry:
        """
        Log a strategy generation request.

        Specialized method for the main use case.
        """
        # Create compliance checks
        compliance_checks = [
            ComplianceCheck(
                check_name="pii_scan",
                status=ComplianceStatus.PASSED if not pii_detected else ComplianceStatus.WARNING,
                details=f"PII detected: {pii_detected}"
            ),
            ComplianceCheck(
                check_name="input_validation",
                status=ComplianceStatus.PASSED,
                details="Input validated successfully"
            ),
        ]

        if response:
            compliance_checks.append(
                ComplianceCheck(
                    check_name="output_quality",
                    status=ComplianceStatus.PASSED if response.quality_metrics.overall_score > 0.7 else ComplianceStatus.WARNING,
                    details=f"Quality score: {response.quality_metrics.overall_score:.2f}"
                )
            )

        return await self.log(
            action=AuditAction.STRATEGY_REQUEST,
            resource="/api/v1/strategy/generate",
            operation="POST",
            correlation_id=correlation_id,
            ip_address=ip_address,
            user_agent=user_agent,
            input_data=request,
            output_data=response,
            model_version=response.metadata.model_version if response else None,
            parameters={
                "industry": request.industry.value,
                "company_stage": request.company_stage.value,
                "focus_area": request.focus_area.value if request.focus_area else None
            },
            status=status,
            error_message=error_message,
            latency_ms=latency_ms,
            pii_detected=pii_detected,
            compliance_checks=compliance_checks
        )

    async def verify_chain(
        self,
        start_index: int = 0,
        end_index: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Verify audit log chain integrity.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self._entries:
            return True, None

        entries = self._entries[start_index:end_index]
        previous_hash = None

        for entry in entries:
            # Reconstruct chain hash
            entry_data = {
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(),
                "action": entry.action.value,
                "correlation_id": entry.correlation_id,
                "input_hash": entry.input_hash
            }
            expected_hash = hashlib.sha256(
                f"{previous_hash}:{json.dumps(entry_data, sort_keys=True, default=str)}".encode()
            ).hexdigest()

            if entry.chain_hash != expected_hash:
                return False, f"Chain broken at entry {entry.id}"

            previous_hash = entry.chain_hash

        return True, None

    async def get_entries(
        self,
        correlation_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> list[AuditEntry]:
        """Query audit entries with filters."""
        results = self._entries

        if correlation_id:
            results = [e for e in results if e.correlation_id == correlation_id]

        if action:
            results = [e for e in results if e.action == action]

        if start_time:
            results = [e for e in results if e.timestamp >= start_time]

        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        return results[-limit:]

    async def get_summary(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> dict:
        """Get summary statistics for a time period."""
        entries = await self.get_entries(
            start_time=start_time,
            end_time=end_time,
            limit=10000
        )

        if not entries:
            return {"total": 0}

        return {
            "total": len(entries),
            "by_action": self._count_by_field(entries, "action"),
            "by_status": self._count_by_field(entries, "status"),
            "pii_detections": sum(1 for e in entries if e.pii_detected),
            "avg_latency_ms": sum(e.latency_ms for e in entries) / len(entries),
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat()
        }

    def _count_by_field(self, entries: list[AuditEntry], field: str) -> dict:
        """Count entries by field value."""
        counts = {}
        for entry in entries:
            value = getattr(entry, field)
            if hasattr(value, "value"):
                value = value.value
            counts[value] = counts.get(value, 0) + 1
        return counts


@lru_cache
def get_audit_logger() -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger()
