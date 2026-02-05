# InnovusX AI Strategy Lab

An enterprise-grade AI platform demonstrating end-to-end ML capabilities, from data ingestion through production deployment with full governance and compliance controls.

## Overview

The InnovusX AI Strategy Lab is an interactive, embeddable AI-powered business strategy assistant that showcases enterprise AI/ML leadership capabilities. Visitors can input their business context and receive personalized growth strategies while exploring the "Under the Hood" panels that reveal the full AI/ML stack.

## Skills Demonstrated

| Skill Area | Implementation |
|------------|----------------|
| **Technical Leadership** | Architecture Decision Records, AI/ML strategy documentation, KPI frameworks |
| **Platform Architecture** | End-to-end pipeline: ingestion → vectors → RAG → agents → serving → monitoring |
| **LLM Expertise** | Fine-tuning configs, prompt engineering, model evaluation, tradeoff analysis |
| **GenAI Systems** | RAG implementation, multi-agent framework, evaluation pipelines, access controls |
| **MLOps & Reliability** | CI/CD pipelines, model registry, drift detection, versioning, monitoring |
| **Compliance & Ethics** | Audit logging, PII detection, bias metrics, model cards, governance policies |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           InnovusX AI Strategy Lab                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Widget    │───▶│   API GW    │───▶│ RAG Engine  │───▶│   Agents    │ │
│  │  (React)    │    │  (FastAPI)  │    │ (LangChain) │    │ (LangGraph) │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │                  │         │
│         ▼                  ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Embed     │    │ Governance  │    │  Vector DB  │    │ LLM Gateway │ │
│  │   Script    │    │   Layer     │    │ (pgvector)  │    │  (Router)   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                            │                                      │         │
│                            ▼                                      ▼         │
│                     ┌─────────────┐                        ┌─────────────┐ │
│                     │   Audit     │                        │   Model     │ │
│                     │   Logging   │                        │  Registry   │ │
│                     └─────────────┘                        └─────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  MLOps: GitHub Actions │ MLflow │ DVC │ Prometheus/Grafana                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
innovusx-ai-platform/
├── docs/                      # Strategy & architecture documentation
│   ├── ARCHITECTURE.md        # System design + component details
│   ├── AI_ML_STRATEGY.md      # Strategic vision + roadmap
│   ├── MLOPS_PRACTICES.md     # MLOps philosophy + implementation
│   ├── GOVERNANCE.md          # Compliance + ethics framework
│   └── adrs/                  # Architecture Decision Records
│
├── api/                       # Backend services (FastAPI)
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Data models
│   │   ├── governance/        # Compliance & audit
│   │   └── monitoring/        # Metrics & observability
│   ├── tests/                 # Test suite
│   └── requirements.txt       # Python dependencies
│
├── widget/                    # Embeddable frontend (React)
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client
│   │   └── embed.tsx          # Embed script entry
│   ├── package.json
│   └── vite.config.ts
│
├── mlops/                     # ML operations
│   ├── pipelines/             # Training & deployment pipelines
│   ├── experiments/           # MLflow experiment configs
│   └── model_cards/           # Model documentation
│
├── data/                      # Data assets (DVC tracked)
│   ├── knowledge_base/        # Strategy knowledge documents
│   ├── embeddings/            # Pre-computed embeddings
│   └── evaluations/           # Evaluation datasets
│
├── infrastructure/            # Deployment configs
│   ├── docker/                # Docker configurations
│   ├── k8s/                   # Kubernetes manifests
│   └── terraform/             # Infrastructure as code
│
└── .github/workflows/         # CI/CD pipelines
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL with pgvector extension

### Local Development

```bash
# Clone and setup
cd innovusx-ai-platform

# Start infrastructure
docker-compose up -d

# Setup API
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Setup Widget (in another terminal)
cd widget
npm install
npm run dev
```

### Environment Variables

```bash
# API Configuration
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
DATABASE_URL=postgresql://localhost:5432/innovusx
REDIS_URL=redis://localhost:6379

# Feature Flags
ENABLE_AUDIT_LOGGING=true
ENABLE_PII_DETECTION=true
ENABLE_DRIFT_MONITORING=true
```

## Embedding the Widget

```html
<!-- Script embed -->
<div id="innovusx-lab"></div>
<script src="https://lab.innovus-x.com/widget.js"></script>
<script>
  InnovusXLab.init({
    container: '#innovusx-lab',
    theme: 'light',
    primaryColor: '#0066cc'
  });
</script>

<!-- Or iframe embed -->
<iframe
  src="https://lab.innovus-x.com/embed"
  width="100%"
  height="800"
  frameborder="0"
></iframe>
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

### RAG Engine
- Document ingestion and chunking
- Semantic search with pgvector
- Hybrid retrieval (dense + sparse)
- Re-ranking for relevance

### Multi-Agent System
- Research Agent: Gathers context and market data
- Strategy Agent: Generates recommendations
- Compliance Agent: Validates outputs
- Orchestration via LangGraph

### Governance
- Complete audit trail for all requests
- PII detection and redaction
- Access control with RBAC
- Bias monitoring and fairness metrics

### MLOps
- Experiment tracking with MLflow
- Data versioning with DVC
- Automated CI/CD pipelines
- Model drift detection

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contact

InnovusX - [innovus-x.com](https://innovus-x.com)
