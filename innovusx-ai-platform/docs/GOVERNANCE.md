# Governance Framework

## Overview

This document defines the governance framework for the InnovusX AI Strategy Lab, covering compliance requirements, ethical guidelines, audit procedures, and risk mitigation strategies.

## Governance Principles

1. **Transparency**: All AI operations are explainable and auditable
2. **Accountability**: Clear ownership for all decisions and outputs
3. **Fairness**: Systems are tested and monitored for bias
4. **Privacy**: User data is protected and minimally collected
5. **Security**: Defense in depth across all layers

## Compliance Framework

### Regulatory Alignment

| Regulation | Applicability | Compliance Measures |
|------------|---------------|---------------------|
| GDPR | EU users | Data minimization, right to deletion |
| CCPA | California users | Disclosure, opt-out mechanisms |
| SOC 2 | Enterprise customers | Security controls, audit trails |
| AI Act (EU) | EU deployment | Risk assessment, transparency |

### Data Governance

**Data Classification**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Data Classification Levels                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │    Public    │  │   Internal   │  │ Confidential │  │  Restricted  │   │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤   │
│  │ • Marketing  │  │ • Business   │  │ • Customer   │  │ • PII        │   │
│  │ • Docs       │  │   metrics    │  │   data       │  │ • Credentials│   │
│  │ • Public API │  │ • Internal   │  │ • API keys   │  │ • Secrets    │   │
│  │   docs       │  │   reports    │  │ • Logs       │  │              │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│        │                 │                 │                 │             │
│        ▼                 ▼                 ▼                 ▼             │
│   No controls       Access control    Encryption +      Encryption +       │
│                                       audit logging    strict access       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data Retention Policy**

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| Request logs | 90 days | Automatic purge |
| Audit logs | 7 years | Manual review required |
| User inputs | 30 days | Automatic purge |
| Generated outputs | 30 days | Automatic purge |
| Analytics (aggregated) | Indefinite | N/A |

### Privacy Controls

**PII Detection and Handling**

```python
# governance/pii_detector.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from dataclasses import dataclass
from enum import Enum

class PIIAction(Enum):
    DETECT = "detect"
    REDACT = "redact"
    REJECT = "reject"

@dataclass
class PIIResult:
    pii_detected: bool
    entities_found: list[dict]
    redacted_text: str | None
    action_taken: PIIAction

class PIIDetector:
    """Detect and handle PII in text inputs."""

    SUPPORTED_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "US_SSN",
        "IP_ADDRESS",
        "LOCATION",
        "DATE_TIME",
    ]

    def __init__(self, action: PIIAction = PIIAction.REDACT):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.action = action

    def process(self, text: str) -> PIIResult:
        """Detect and optionally redact PII."""
        # Analyze text for PII
        results = self.analyzer.analyze(
            text=text,
            entities=self.SUPPORTED_ENTITIES,
            language="en"
        )

        entities_found = [
            {
                "type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score
            }
            for r in results
        ]

        pii_detected = len(entities_found) > 0
        redacted_text = None

        if pii_detected and self.action == PIIAction.REDACT:
            anonymized = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            redacted_text = anonymized.text

        return PIIResult(
            pii_detected=pii_detected,
            entities_found=entities_found,
            redacted_text=redacted_text,
            action_taken=self.action if pii_detected else PIIAction.DETECT
        )
```

## Audit System

### Audit Log Schema

```python
# governance/audit.py
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
import hashlib
import json

class AuditAction(Enum):
    STRATEGY_REQUEST = "strategy_request"
    STRATEGY_RESPONSE = "strategy_response"
    MODEL_INFERENCE = "model_inference"
    DATA_ACCESS = "data_access"
    CONFIG_CHANGE = "config_change"
    AUTH_EVENT = "auth_event"

class AuditEntry(BaseModel):
    """Immutable audit log entry."""

    # Identification
    id: str
    correlation_id: str
    timestamp: datetime

    # Action details
    action: AuditAction
    resource: str
    operation: str

    # Actor
    user_id: str | None
    api_key_id: str | None
    ip_address: str
    user_agent: str

    # Request/Response
    input_hash: str  # SHA-256 of input
    output_hash: str | None  # SHA-256 of output

    # Context
    model_version: str | None
    parameters: dict

    # Results
    status: str  # success, failure, blocked
    error_message: str | None
    latency_ms: int

    # Compliance
    pii_detected: bool
    pii_entities: list[str]
    compliance_checks: dict[str, bool]

    class Config:
        frozen = True  # Immutable

class AuditLogger:
    """Audit logging system with tamper detection."""

    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.previous_hash = None

    def log(self, entry: AuditEntry) -> str:
        """Log an audit entry with chain verification."""
        # Create chain hash for tamper detection
        entry_json = entry.model_dump_json()
        chain_data = f"{self.previous_hash}:{entry_json}"
        chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()

        # Store entry with chain hash
        stored_entry = {
            "entry": entry.model_dump(),
            "chain_hash": chain_hash,
            "previous_hash": self.previous_hash
        }

        self.storage.write(entry.id, stored_entry)
        self.previous_hash = chain_hash

        return entry.id

    def verify_chain(self, start_id: str, end_id: str) -> bool:
        """Verify audit log chain integrity."""
        entries = self.storage.read_range(start_id, end_id)

        previous_hash = None
        for entry_data in entries:
            entry_json = json.dumps(entry_data["entry"], sort_keys=True)
            expected_hash = hashlib.sha256(
                f"{previous_hash}:{entry_json}".encode()
            ).hexdigest()

            if entry_data["chain_hash"] != expected_hash:
                return False

            previous_hash = entry_data["chain_hash"]

        return True
```

### Audit Trail Visualization

```
Request Timeline:
─────────────────────────────────────────────────────────────────────────────
│
│  09:42:01.234  ──┬── REQUEST_RECEIVED
│                  │   correlation_id: req-abc123
│                  │   user: anonymous
│                  │   ip: 192.168.1.100
│                  │
│  09:42:01.256  ──┼── PII_SCAN
│                  │   status: passed
│                  │   entities_detected: 0
│                  │
│  09:42:01.312  ──┼── INPUT_VALIDATION
│                  │   status: passed
│                  │   schema_version: v2
│                  │
│  09:42:01.456  ──┼── RAG_RETRIEVAL
│                  │   documents_retrieved: 12
│                  │   top_score: 0.89
│                  │
│  09:42:02.341  ──┼── MODEL_INFERENCE
│                  │   model: gpt-4-turbo
│                  │   version: v2.3
│                  │   tokens: 856
│                  │
│  09:42:03.012  ──┼── OUTPUT_VALIDATION
│                  │   status: passed
│                  │   safety_score: 0.98
│                  │
│  09:42:03.102  ──┼── COMPLIANCE_CHECK
│                  │   bias_score: 0.02
│                  │   policy_violations: 0
│                  │
│  09:42:03.234  ──┴── RESPONSE_SENT
│                      latency_ms: 2000
│                      status: success
│
─────────────────────────────────────────────────────────────────────────────
```

## Access Control

### Role-Based Access Control (RBAC)

```python
# governance/access_control.py
from enum import Enum
from dataclasses import dataclass

class Permission(Enum):
    # Strategy operations
    STRATEGY_READ = "strategy:read"
    STRATEGY_GENERATE = "strategy:generate"

    # Admin operations
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"

    # Audit operations
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # Model operations
    MODEL_READ = "model:read"
    MODEL_DEPLOY = "model:deploy"

class Role(Enum):
    ANONYMOUS = "anonymous"
    USER = "user"
    DEVELOPER = "developer"
    ADMIN = "admin"

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ANONYMOUS: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
    },
    Role.USER: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
    },
    Role.DEVELOPER: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
        Permission.CONFIG_READ,
        Permission.AUDIT_READ,
        Permission.MODEL_READ,
    },
    Role.ADMIN: {
        Permission.STRATEGY_READ,
        Permission.STRATEGY_GENERATE,
        Permission.CONFIG_READ,
        Permission.CONFIG_WRITE,
        Permission.AUDIT_READ,
        Permission.AUDIT_EXPORT,
        Permission.MODEL_READ,
        Permission.MODEL_DEPLOY,
    },
}

@dataclass
class AccessContext:
    user_id: str | None
    role: Role
    api_key_id: str | None
    permissions: set[Permission]

class AccessController:
    """Enforce access control policies."""

    def __init__(self):
        self.role_permissions = ROLE_PERMISSIONS

    def check_permission(
        self,
        context: AccessContext,
        required: Permission
    ) -> bool:
        """Check if context has required permission."""
        return required in context.permissions

    def get_context_from_api_key(self, api_key: str) -> AccessContext:
        """Resolve API key to access context."""
        # Look up API key in database
        key_data = self._lookup_api_key(api_key)

        if not key_data:
            return AccessContext(
                user_id=None,
                role=Role.ANONYMOUS,
                api_key_id=None,
                permissions=self.role_permissions[Role.ANONYMOUS]
            )

        role = Role(key_data["role"])
        return AccessContext(
            user_id=key_data["user_id"],
            role=role,
            api_key_id=key_data["id"],
            permissions=self.role_permissions[role]
        )
```

### API Key Management

```yaml
# API Key Scopes
api_keys:
  - id: key_demo_001
    name: "Demo Widget"
    role: anonymous
    rate_limit: 100/hour
    allowed_origins:
      - "https://innovus-x.com"
      - "http://localhost:*"

  - id: key_prod_001
    name: "Production Widget"
    role: user
    rate_limit: 1000/hour
    allowed_origins:
      - "https://innovus-x.com"

  - id: key_admin_001
    name: "Admin Access"
    role: admin
    rate_limit: unlimited
    allowed_origins:
      - "*"
    requires_mfa: true
```

## Ethical AI Guidelines

### Bias Monitoring

```python
# governance/bias_monitor.py
from dataclasses import dataclass
import numpy as np

@dataclass
class BiasMetrics:
    demographic_parity: float  # Difference in positive rates
    equalized_odds: float      # Difference in TPR/FPR
    individual_fairness: float # Similar inputs → similar outputs
    overall_score: float

class BiasMonitor:
    """Monitor AI outputs for potential bias."""

    PROTECTED_ATTRIBUTES = [
        "industry",      # Should not favor certain industries
        "company_size",  # Should not favor large over small
        "geography",     # Should not favor certain regions
    ]

    THRESHOLD = 0.1  # Maximum acceptable bias score

    def evaluate(
        self,
        inputs: list[dict],
        outputs: list[dict]
    ) -> BiasMetrics:
        """Evaluate outputs for bias across protected attributes."""
        scores = []

        for attribute in self.PROTECTED_ATTRIBUTES:
            # Group outputs by attribute value
            groups = self._group_by_attribute(inputs, outputs, attribute)

            # Calculate quality scores per group
            group_scores = {
                group: np.mean([o["quality_score"] for o in outputs])
                for group, outputs in groups.items()
            }

            # Calculate disparity
            max_score = max(group_scores.values())
            min_score = min(group_scores.values())
            disparity = max_score - min_score

            scores.append(disparity)

        return BiasMetrics(
            demographic_parity=scores[0] if scores else 0,
            equalized_odds=scores[1] if len(scores) > 1 else 0,
            individual_fairness=self._calculate_individual_fairness(
                inputs, outputs
            ),
            overall_score=np.mean(scores) if scores else 0
        )

    def _calculate_individual_fairness(
        self,
        inputs: list[dict],
        outputs: list[dict]
    ) -> float:
        """Similar inputs should produce similar outputs."""
        # Implementation: cosine similarity of input embeddings
        # vs output similarity
        pass
```

### Content Safety

```python
# governance/safety.py
from enum import Enum
from dataclasses import dataclass

class SafetyCategory(Enum):
    HARMFUL_ADVICE = "harmful_advice"
    FINANCIAL_RISK = "financial_risk"
    LEGAL_RISK = "legal_risk"
    DISCRIMINATION = "discrimination"
    MISINFORMATION = "misinformation"

@dataclass
class SafetyResult:
    is_safe: bool
    categories_flagged: list[SafetyCategory]
    confidence: float
    explanation: str

class SafetyChecker:
    """Check AI outputs for safety concerns."""

    PROHIBITED_PATTERNS = [
        # Financial
        r"guaranteed.*return",
        r"risk.free.*investment",
        # Legal
        r"definitely.*legal",
        r"no.*liability",
        # Discriminatory
        r"only.*hire",
        r"don't.*work with",
    ]

    def check(self, output: str) -> SafetyResult:
        """Check output for safety concerns."""
        flagged = []

        # Pattern matching
        for pattern in self.PROHIBITED_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                flagged.append(self._categorize_pattern(pattern))

        # LLM-based safety check for nuanced issues
        llm_result = self._llm_safety_check(output)
        flagged.extend(llm_result.categories)

        return SafetyResult(
            is_safe=len(flagged) == 0,
            categories_flagged=list(set(flagged)),
            confidence=llm_result.confidence,
            explanation=llm_result.explanation
        )
```

## Risk Management

### Risk Register

| Risk ID | Risk | Impact | Likelihood | Mitigation | Owner |
|---------|------|--------|------------|------------|-------|
| R001 | Model generates harmful advice | High | Low | Safety checker, human review | ML Lead |
| R002 | PII leakage in outputs | High | Medium | PII detection, redaction | Security |
| R003 | Biased recommendations | Medium | Medium | Bias monitoring, diverse training | ML Lead |
| R004 | System unavailability | Medium | Low | Multi-region deployment | Platform |
| R005 | API key compromise | High | Low | Key rotation, rate limiting | Security |
| R006 | Data breach | High | Low | Encryption, access controls | Security |
| R007 | Regulatory non-compliance | High | Medium | Compliance audits, documentation | Legal |

### Incident Response Plan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Incident Response Workflow                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ Detect   │───▶│ Assess   │───▶│ Contain  │───▶│ Resolve  │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│       │              │                │               │                     │
│       ▼              ▼                ▼               ▼                     │
│  Monitoring      Severity         Isolate         Fix root                  │
│  alerts          rating           impact          cause                     │
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                              │
│  │ Document │───▶│ Review   │───▶│ Improve  │                              │
│  └──────────┘    └──────────┘    └──────────┘                              │
│       │              │                │                                     │
│       ▼              ▼                ▼                                     │
│  Incident        Post-mortem     Update                                     │
│  report          analysis        controls                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Compliance Reporting

### Monthly Governance Report Template

```markdown
# Governance Report - [Month Year]

## Executive Summary
- Overall compliance score: X/100
- Incidents: X (X resolved)
- Audit findings: X

## Metrics

### Privacy
- PII detections: X
- PII incidents: X
- Data deletion requests: X (X completed)

### Security
- Authentication failures: X
- Rate limit violations: X
- Suspicious activity alerts: X

### Fairness
- Average bias score: X.XX (threshold: 0.10)
- Groups monitored: X
- Bias alerts: X

### Audit
- Total requests logged: X
- Audit chain integrity: ✓/✗
- Compliance checks passed: X%

## Incidents
| Date | Severity | Description | Status |
|------|----------|-------------|--------|
| ... | ... | ... | ... |

## Recommendations
1. ...
2. ...

## Next Period Focus
1. ...
2. ...
```

## Related Documents

- [Architecture](ARCHITECTURE.md)
- [AI/ML Strategy](AI_ML_STRATEGY.md)
- [MLOps Practices](MLOPS_PRACTICES.md)
