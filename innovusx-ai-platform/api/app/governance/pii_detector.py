"""PII (Personally Identifiable Information) detection and handling."""

import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Optional

import structlog

from app.config import settings

logger = structlog.get_logger()


class PIIAction(str, Enum):
    """Actions to take when PII is detected."""
    DETECT = "detect"    # Just detect, don't modify
    REDACT = "redact"    # Replace with placeholder
    BLOCK = "block"      # Reject the request


class PIIEntityType(str, Enum):
    """Types of PII entities."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    PERSON_NAME = "person_name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"


@dataclass
class PIIEntity:
    """A detected PII entity."""
    entity_type: PIIEntityType
    start: int
    end: int
    text: str
    confidence: float


@dataclass
class PIIResult:
    """Result of PII detection."""
    pii_detected: bool
    entities: list[PIIEntity]
    original_text: str
    redacted_text: Optional[str]
    action_taken: str


class PIIDetector:
    """
    PII detection and handling service.

    Uses pattern matching for common PII types.
    In production, integrate with Microsoft Presidio or
    similar NER-based detection.
    """

    # Regex patterns for common PII
    PATTERNS = {
        PIIEntityType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIEntityType.PHONE: r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b',
        PIIEntityType.SSN: r'\b(?!000|666|9\d{2})\d{3}[-]?(?!00)\d{2}[-]?(?!0000)\d{4}\b',
        PIIEntityType.CREDIT_CARD: r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        PIIEntityType.IP_ADDRESS: r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    }

    # Redaction placeholders
    REDACTION_PLACEHOLDERS = {
        PIIEntityType.EMAIL: "[EMAIL_REDACTED]",
        PIIEntityType.PHONE: "[PHONE_REDACTED]",
        PIIEntityType.SSN: "[SSN_REDACTED]",
        PIIEntityType.CREDIT_CARD: "[CREDIT_CARD_REDACTED]",
        PIIEntityType.IP_ADDRESS: "[IP_REDACTED]",
        PIIEntityType.PERSON_NAME: "[NAME_REDACTED]",
        PIIEntityType.ADDRESS: "[ADDRESS_REDACTED]",
        PIIEntityType.DATE_OF_BIRTH: "[DOB_REDACTED]",
    }

    def __init__(
        self,
        default_action: PIIAction = PIIAction.REDACT,
        enabled: bool = True
    ):
        self.default_action = default_action
        self.enabled = enabled and settings.enable_pii_detection

        # Compile patterns for efficiency
        self._compiled_patterns = {
            entity_type: re.compile(pattern)
            for entity_type, pattern in self.PATTERNS.items()
        }

        logger.info(
            "PII detector initialized",
            enabled=self.enabled,
            default_action=default_action.value
        )

    async def scan(
        self,
        text: str,
        action: Optional[PIIAction] = None,
        correlation_id: str = ""
    ) -> PIIResult:
        """
        Scan text for PII and optionally redact.

        Args:
            text: Text to scan
            action: Action to take if PII found
            correlation_id: Request correlation ID

        Returns:
            PIIResult with detection results
        """
        if not self.enabled:
            return PIIResult(
                pii_detected=False,
                entities=[],
                original_text=text,
                redacted_text=text,
                action_taken="skipped"
            )

        action = action or self.default_action
        entities = []

        # Detect PII using patterns
        for entity_type, pattern in self._compiled_patterns.items():
            for match in pattern.finditer(text):
                entities.append(PIIEntity(
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    confidence=0.95  # Pattern matching is high confidence
                ))

        pii_detected = len(entities) > 0

        if pii_detected:
            logger.warning(
                "PII detected",
                correlation_id=correlation_id,
                entity_count=len(entities),
                entity_types=[e.entity_type.value for e in entities]
            )

        # Determine action
        redacted_text = text
        action_taken = action.value

        if pii_detected:
            if action == PIIAction.REDACT:
                redacted_text = self._redact(text, entities)
            elif action == PIIAction.BLOCK:
                action_taken = "blocked"

        return PIIResult(
            pii_detected=pii_detected,
            entities=entities,
            original_text=text,
            redacted_text=redacted_text,
            action_taken=action_taken
        )

    def _redact(self, text: str, entities: list[PIIEntity]) -> str:
        """Redact PII entities from text."""
        # Sort entities by position (reverse) to maintain indices
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)

        result = text
        for entity in sorted_entities:
            placeholder = self.REDACTION_PLACEHOLDERS.get(
                entity.entity_type,
                "[PII_REDACTED]"
            )
            result = result[:entity.start] + placeholder + result[entity.end:]

        return result

    async def validate_no_pii(
        self,
        text: str,
        correlation_id: str = ""
    ) -> tuple[bool, list[str]]:
        """
        Validate that text contains no PII.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        result = await self.scan(text, PIIAction.DETECT, correlation_id)

        issues = []
        if result.pii_detected:
            for entity in result.entities:
                issues.append(
                    f"Found {entity.entity_type.value} at position {entity.start}"
                )

        return not result.pii_detected, issues

    async def scan_batch(
        self,
        texts: list[str],
        correlation_id: str = ""
    ) -> list[PIIResult]:
        """Scan multiple texts for PII."""
        return [
            await self.scan(text, correlation_id=correlation_id)
            for text in texts
        ]

    def add_custom_pattern(
        self,
        entity_type: PIIEntityType,
        pattern: str,
        placeholder: str
    ) -> None:
        """Add a custom pattern for PII detection."""
        self._compiled_patterns[entity_type] = re.compile(pattern)
        self.REDACTION_PLACEHOLDERS[entity_type] = placeholder

        logger.info(
            "Custom PII pattern added",
            entity_type=entity_type.value
        )


@lru_cache
def get_pii_detector() -> PIIDetector:
    """Get PII detector instance."""
    return PIIDetector()
