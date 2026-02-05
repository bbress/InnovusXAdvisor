# MLOps Practices

## Overview

This document defines the MLOps philosophy, practices, and implementation details for the InnovusX AI Strategy Lab. It covers the full ML lifecycle from experimentation to production monitoring.

## MLOps Maturity Model

We follow a progressive maturity model for ML operations:

```
Level 0: Manual           Level 1: ML Pipeline      Level 2: CI/CD          Level 3: Full MLOps
──────────────────────────────────────────────────────────────────────────────────────────────
• Manual training         • Automated training      • Automated testing      • Automated retraining
• Manual deployment       • Manual deployment       • Automated deployment   • Automated monitoring
• No versioning          • Data versioning         • Model versioning       • Drift detection
• No monitoring          • Basic metrics           • Comprehensive metrics  • Self-healing

Current State: Level 2 → Target: Level 3
```

## ML Lifecycle

### 1. Data Management

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Data Pipeline                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  Ingest  │───▶│ Validate │───▶│Transform │───▶│  Store   │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│       │              │                │               │                     │
│       ▼              ▼                ▼               ▼                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ Sources  │    │  Schema  │    │ Features │    │  DVC     │             │
│  │ • Docs   │    │  Checks  │    │ Engineer │    │ Tracked  │             │
│  │ • APIs   │    │  Quality │    │          │    │          │             │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data Versioning (DVC)**

```yaml
# dvc.yaml
stages:
  prepare_knowledge_base:
    cmd: python scripts/prepare_data.py
    deps:
      - data/raw/
    outs:
      - data/processed/knowledge_base.json

  generate_embeddings:
    cmd: python scripts/generate_embeddings.py
    deps:
      - data/processed/knowledge_base.json
    outs:
      - data/embeddings/
    metrics:
      - metrics/embedding_quality.json
```

**Data Quality Checks**

```python
# data_validation.py
from great_expectations import DataContext

def validate_knowledge_base(data: list[dict]) -> bool:
    """Validate knowledge base entries."""
    checks = [
        # Schema validation
        all(required_fields <= set(item.keys()) for item in data),
        # Content validation
        all(len(item['content']) > 100 for item in data),
        # No duplicates
        len(data) == len(set(item['id'] for item in data)),
        # Category coverage
        len(set(item['category'] for item in data)) >= 5,
    ]
    return all(checks)
```

### 2. Experiment Tracking

**MLflow Configuration**

```python
# mlflow_config.py
import mlflow

mlflow.set_tracking_uri("http://mlflow.internal:5000")
mlflow.set_experiment("strategy-advisor")

def log_experiment(
    params: dict,
    metrics: dict,
    artifacts: list[str],
    model_name: str = None
):
    """Log an experiment run."""
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        for artifact in artifacts:
            mlflow.log_artifact(artifact)

        if model_name:
            mlflow.register_model(
                f"runs:/{mlflow.active_run().info.run_id}/model",
                model_name
            )
```

**Experiment Structure**

```
experiments/
├── baseline/
│   ├── config.yaml
│   ├── run.py
│   └── results/
├── rag_improvements/
│   ├── hybrid_retrieval/
│   ├── reranking_comparison/
│   └── chunk_size_ablation/
└── prompt_engineering/
    ├── system_prompts/
    ├── few_shot_examples/
    └── output_formats/
```

### 3. Model Registry

**Model Lifecycle Stages**

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   None   │───▶│ Staging  │───▶│Production│───▶│ Archived │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               │
     ▼               ▼               ▼               ▼
  Trained       Validated       Deployed        Retired
  model         & tested        to prod         from use
```

**Model Card Template**

```yaml
# model_cards/strategy-advisor-v2.3.yaml
model_name: strategy-advisor
version: "2.3"
created_date: "2024-01-15"
last_updated: "2024-01-15"

model_details:
  description: "RAG-based business strategy recommendation system"
  architecture: "GPT-4 Turbo with retrieval augmentation"
  input_format: "JSON with industry, stage, challenge, focus"
  output_format: "JSON with strategies array and metadata"

intended_use:
  primary_uses:
    - "Business strategy recommendation"
    - "Growth opportunity identification"
  out_of_scope:
    - "Financial advice"
    - "Legal guidance"
    - "Personal decisions"

training_data:
  description: "Curated business strategy knowledge base"
  size: "847 documents"
  sources:
    - "Business case studies"
    - "Industry reports"
    - "Growth frameworks"
  preprocessing: "Chunked to 512 tokens with 50 overlap"

evaluation:
  metrics:
    relevance: 0.89
    groundedness: 0.94
    coherence: 0.91
    actionability: 0.85
  test_set_size: 200
  evaluation_date: "2024-01-14"

ethical_considerations:
  bias_evaluation: "Tested across industries and company sizes"
  limitations:
    - "May not cover niche industries"
    - "Recommendations are general guidance"
  risks:
    - "Over-reliance on AI recommendations"

deployment:
  infrastructure: "Kubernetes on GCP"
  scaling: "Horizontal pod autoscaling"
  monitoring: "Prometheus + Grafana"
```

### 4. CI/CD Pipelines

**Pipeline Architecture**

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    paths:
      - 'data/**'
      - 'mlops/**'
      - 'api/app/services/**'

jobs:
  data-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate data
        run: python scripts/validate_data.py

  model-evaluation:
    needs: data-validation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run evaluation suite
        run: python mlops/pipelines/evaluation.py
      - name: Upload metrics
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-metrics
          path: metrics/

  staging-deployment:
    needs: model-evaluation
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          kubectl apply -f infrastructure/k8s/staging/
      - name: Run smoke tests
        run: python tests/smoke_tests.py

  production-deployment:
    needs: staging-deployment
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Blue-green deployment
        run: |
          ./scripts/blue-green-deploy.sh
      - name: Verify deployment
        run: python tests/production_verification.py
```

**Deployment Strategy**

```bash
#!/bin/bash
# blue-green-deploy.sh

# 1. Deploy new version (green)
kubectl apply -f infrastructure/k8s/production/green/

# 2. Wait for green to be healthy
kubectl wait --for=condition=ready pod -l version=green --timeout=300s

# 3. Run canary tests
python tests/canary_tests.py

# 4. Switch traffic to green
kubectl patch service api-service -p '{"spec":{"selector":{"version":"green"}}}'

# 5. Verify traffic switch
sleep 30
python tests/traffic_verification.py

# 6. Scale down blue
kubectl scale deployment api-blue --replicas=0
```

### 5. Monitoring & Observability

**Metrics Collection**

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
REQUEST_COUNT = Counter(
    'strategy_requests_total',
    'Total strategy generation requests',
    ['status', 'model_version']
)

REQUEST_LATENCY = Histogram(
    'strategy_request_latency_seconds',
    'Request latency in seconds',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Model metrics
MODEL_INFERENCE_TIME = Histogram(
    'model_inference_seconds',
    'Model inference time',
    ['model_name']
)

TOKEN_USAGE = Counter(
    'token_usage_total',
    'Total tokens used',
    ['model_name', 'token_type']
)

# Quality metrics
QUALITY_SCORE = Gauge(
    'strategy_quality_score',
    'Quality score of generated strategies',
    ['metric_name']
)

# Drift metrics
EMBEDDING_DRIFT = Gauge(
    'embedding_drift_score',
    'Drift score for embeddings'
)

RESPONSE_DRIFT = Gauge(
    'response_drift_score',
    'Drift score for responses'
)
```

**Drift Detection**

```python
# monitoring/drift.py
import numpy as np
from scipy import stats
from dataclasses import dataclass

@dataclass
class DriftResult:
    drift_detected: bool
    drift_score: float
    p_value: float
    threshold: float

class DriftDetector:
    def __init__(self, reference_data: np.ndarray, threshold: float = 0.05):
        self.reference_data = reference_data
        self.threshold = threshold

    def detect_drift(self, current_data: np.ndarray) -> DriftResult:
        """Detect distribution drift using KS test."""
        statistic, p_value = stats.ks_2samp(
            self.reference_data.flatten(),
            current_data.flatten()
        )

        return DriftResult(
            drift_detected=p_value < self.threshold,
            drift_score=statistic,
            p_value=p_value,
            threshold=self.threshold
        )

class EmbeddingDriftMonitor:
    def __init__(self, reference_embeddings: np.ndarray):
        self.detector = DriftDetector(reference_embeddings)
        self.history = []

    def check(self, current_embeddings: np.ndarray) -> DriftResult:
        result = self.detector.detect_drift(current_embeddings)
        self.history.append(result)

        # Update Prometheus metric
        EMBEDDING_DRIFT.set(result.drift_score)

        if result.drift_detected:
            self._alert(result)

        return result

    def _alert(self, result: DriftResult):
        """Send alert when drift detected."""
        # Integration with alerting system
        pass
```

**Grafana Dashboard Configuration**

```json
{
  "dashboard": {
    "title": "InnovusX AI Platform",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(strategy_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Latency P99",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(strategy_request_latency_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Quality Scores",
        "type": "gauge",
        "targets": [
          {
            "expr": "strategy_quality_score"
          }
        ]
      },
      {
        "title": "Drift Detection",
        "type": "stat",
        "targets": [
          {
            "expr": "embedding_drift_score"
          }
        ],
        "thresholds": {
          "steps": [
            {"value": 0, "color": "green"},
            {"value": 0.1, "color": "yellow"},
            {"value": 0.2, "color": "red"}
          ]
        }
      }
    ]
  }
}
```

### 6. Incident Response

**Runbook: Model Performance Degradation**

```markdown
## Incident: Model Performance Degradation

### Detection
- Alert: `strategy_quality_score < 0.8 for 15 minutes`
- Dashboard: Quality Scores panel showing decline

### Immediate Actions
1. Check recent deployments
   ```bash
   kubectl rollout history deployment/api
   ```

2. Review error logs
   ```bash
   kubectl logs -l app=api --since=1h | grep ERROR
   ```

3. Check upstream dependencies
   - OpenAI API status: https://status.openai.com
   - Database connectivity

### Investigation
1. Compare current vs baseline metrics
2. Sample recent requests for manual review
3. Check for data drift

### Mitigation
1. If deployment-related: Rollback
   ```bash
   kubectl rollout undo deployment/api
   ```

2. If model-related: Switch to fallback
   ```bash
   kubectl set env deployment/api LLM_PRIMARY=claude-3
   ```

3. If data-related: Revert to known-good embeddings

### Post-Incident
1. Document root cause
2. Update monitoring thresholds
3. Add regression test
```

## Tools & Infrastructure

### Tool Stack

| Category | Tool | Purpose |
|----------|------|---------|
| Experiment Tracking | MLflow | Log experiments, compare runs |
| Data Versioning | DVC | Version datasets and models |
| Pipeline Orchestration | GitHub Actions | CI/CD automation |
| Model Serving | FastAPI + Uvicorn | Low-latency inference |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| Logging | Structured JSON + ELK | Centralized logging |
| Alerting | PagerDuty | Incident management |

### Environment Parity

```
Development → Staging → Production
     │            │           │
     ▼            ▼           ▼
Docker Compose  K8s (small)  K8s (full)
SQLite          PostgreSQL   Cloud SQL
Local Redis     Redis        MemoryStore
```

## Best Practices Summary

1. **Version Everything**: Code, data, models, configs
2. **Automate Relentlessly**: If you do it twice, automate it
3. **Monitor Proactively**: Detect issues before users do
4. **Test Thoroughly**: Unit, integration, smoke, canary
5. **Document Decisions**: ADRs for significant choices
6. **Review Continuously**: Regular model performance reviews
7. **Plan for Failure**: Graceful degradation, rollback procedures

## Related Documents

- [Architecture](ARCHITECTURE.md)
- [AI/ML Strategy](AI_ML_STRATEGY.md)
- [Governance](GOVERNANCE.md)
