# Architecture Documentation

## System Overview

The InnovusX AI Strategy Lab is designed as a modular, scalable platform that demonstrates enterprise-grade AI/ML capabilities. This document details the architectural decisions, component interactions, and design principles.

## Design Principles

1. **Separation of Concerns**: Each component has a single responsibility
2. **Observability First**: Every operation is logged, traced, and measurable
3. **Security by Default**: Zero-trust architecture with audit trails
4. **Graceful Degradation**: System continues operating under partial failure
5. **Configuration over Code**: Behavior changes without deployments

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                  │
│  │  Web Widget    │  │  iframe Embed  │  │   Direct API   │                  │
│  │   (React)      │  │                │  │    Clients     │                  │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                  │
│          │                   │                   │                            │
│          └───────────────────┼───────────────────┘                            │
│                              ▼                                                │
├──────────────────────────────────────────────────────────────────────────────┤
│                              API Gateway                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                         FastAPI Application                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │   /strategy  │  │  /telemetry  │  │    /audit    │                  │  │
│  │  │    Router    │  │    Router    │  │    Router    │                  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │  │
│  │                              │                                          │  │
│  │  ┌────────────────────────────────────────────────────────────────┐    │  │
│  │  │                    Middleware Stack                             │    │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │    │  │
│  │  │  │  Auth   │ │  Rate   │ │  CORS   │ │ Logging │ │ Tracing │  │    │  │
│  │  │  │         │ │  Limit  │ │         │ │         │ │         │  │    │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │    │  │
│  │  └────────────────────────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│                            Service Layer                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  RAG Engine  │  │    Agent     │  │     LLM      │  │  Evaluation  │     │
│  │              │  │ Orchestrator │  │   Gateway    │  │    Engine    │     │
│  │  • Ingest    │  │              │  │              │  │              │     │
│  │  • Chunk     │  │  • Research  │  │  • Routing   │  │  • Quality   │     │
│  │  • Embed     │  │  • Strategy  │  │  • Fallback  │  │  • Latency   │     │
│  │  • Retrieve  │  │  • Compliance│  │  • Caching   │  │  • Cost      │     │
│  │  • Rerank    │  │              │  │              │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │                 │              │
├─────────┼─────────────────┼─────────────────┼─────────────────┼──────────────┤
│         │           Governance Layer        │                 │              │
├─────────┼─────────────────────────────────────────────────────┼──────────────┤
│  ┌──────┴───────┐  ┌──────────────┐  ┌──────────────┐  ┌──────┴───────┐     │
│  │    Audit     │  │     PII      │  │    Access    │  │     Bias     │     │
│  │   Logger     │  │   Detector   │  │   Control    │  │   Monitor    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
├──────────────────────────────────────────────────────────────────────────────┤
│                            Data Layer                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Redis     │  │   MLflow     │  │ Prometheus   │     │
│  │  + pgvector  │  │    Cache     │  │   Tracking   │  │   Metrics    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Gateway (FastAPI)

The API gateway handles all incoming requests with comprehensive middleware:

```python
# Request flow
Request → Auth → RateLimit → CORS → Logging → Tracing → Router → Response
```

**Key Features:**
- JWT-based authentication for API clients
- Rate limiting per API key (100 req/min default)
- CORS configuration for widget embedding
- Structured logging with correlation IDs
- OpenTelemetry tracing integration

### 2. RAG Engine

The Retrieval-Augmented Generation engine provides context-aware responses:

```
Document → Chunking → Embedding → Vector Store
                                       ↓
Query → Embedding → Retrieval → Reranking → Context
```

**Configuration:**
- Chunk size: 512 tokens with 50 token overlap
- Embedding model: text-embedding-3-small (1536 dimensions)
- Retrieval: Hybrid (dense + BM25 sparse)
- Top-k retrieval: 10 documents
- Reranking: Cross-encoder reranking to top 5

### 3. Agent Orchestrator

Multi-agent system using LangGraph for complex reasoning:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │Research │───▶│Strategy │───▶│Compliance│                  │
│  │ Agent   │    │  Agent  │    │  Agent   │                  │
│  └─────────┘    └─────────┘    └─────────┘                  │
│       │              │              │                        │
│       ▼              ▼              ▼                        │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                  │
│  │ Search  │    │   RAG   │    │ Policy  │                  │
│  │  Tools  │    │  Tools  │    │  Check  │                  │
│  └─────────┘    └─────────┘    └─────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

**Agents:**
- **Research Agent**: Gathers industry context, market data, competitor info
- **Strategy Agent**: Synthesizes recommendations using RAG context
- **Compliance Agent**: Validates outputs against policy rules

### 4. LLM Gateway

Intelligent routing and management of LLM calls:

```python
class LLMGateway:
    def route(self, request):
        # 1. Check cache
        # 2. Select model based on request type
        # 3. Apply rate limiting
        # 4. Execute with fallback
        # 5. Log metrics
```

**Features:**
- Model routing based on task complexity
- Automatic fallback: GPT-4 → Claude → GPT-3.5
- Response caching (5-minute TTL)
- Token usage tracking
- Cost optimization

### 5. Governance Layer

Comprehensive compliance and audit infrastructure:

**Audit Logger:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "req-abc123",
  "action": "strategy_generation",
  "user_id": "anonymous",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "model_version": "v2.3",
  "latency_ms": 1234,
  "tokens_used": 856,
  "pii_detected": false,
  "compliance_status": "passed"
}
```

**PII Detector:**
- Uses Microsoft Presidio for entity detection
- Detects: emails, phone numbers, SSN, credit cards, names
- Action: Redact before processing, log detection

**Access Control:**
- RBAC with predefined roles
- API key scopes: read, write, admin
- Request signing for sensitive operations

### 6. Evaluation Engine

Continuous quality assessment:

**Metrics:**
| Metric | Description | Target |
|--------|-------------|--------|
| Relevance | Answer addresses the question | > 0.85 |
| Groundedness | Claims supported by context | > 0.90 |
| Coherence | Logical flow and clarity | > 0.85 |
| Actionability | Specific, implementable advice | > 0.80 |

**Implementation:**
- LLM-as-judge for quality scoring
- A/B testing framework for experiments
- Human feedback collection

## Data Flow

### Strategy Generation Request

```
1. Client sends POST /api/v1/strategy/generate
   {
     "industry": "fintech",
     "company_stage": "growth",
     "challenge": "international expansion",
     "focus_area": "market_expansion"
   }

2. Middleware processes request
   - Validate auth token
   - Check rate limits
   - Log request start
   - Generate correlation ID

3. Strategy Router receives request
   - Validate input schema
   - Check for cached response
   - Forward to service layer

4. RAG Engine retrieves context
   - Embed query
   - Search vector store (top 10)
   - Rerank results (top 5)
   - Return context documents

5. Agent Orchestrator processes
   - Research Agent: Enhance context
   - Strategy Agent: Generate strategies
   - Compliance Agent: Validate output

6. Evaluation Engine scores response
   - Calculate quality metrics
   - Log evaluation results

7. Governance checks
   - PII scan on output
   - Audit log entry
   - Bias metric calculation

8. Response returned to client
   {
     "strategies": [...],
     "metadata": {
       "model_version": "v2.3",
       "latency_ms": 1234,
       "quality_scores": {...}
     }
   }
```

## Scalability Considerations

### Horizontal Scaling
- API: Stateless, scale with load balancer
- Workers: Queue-based async processing
- Database: Read replicas for queries

### Caching Strategy
- L1: In-memory (API instance)
- L2: Redis (shared across instances)
- L3: CDN (static assets, embeddings)

### Performance Targets
| Metric | Target | Current |
|--------|--------|---------|
| P50 Latency | < 1s | 0.8s |
| P99 Latency | < 3s | 2.5s |
| Throughput | 100 req/s | 120 req/s |
| Availability | 99.9% | 99.95% |

## Security Architecture

### Defense in Depth
1. **Network**: WAF, DDoS protection
2. **Transport**: TLS 1.3, certificate pinning
3. **Application**: Input validation, output encoding
4. **Data**: Encryption at rest, field-level encryption
5. **Access**: RBAC, principle of least privilege

### Threat Model
- Input injection: Mitigated by strict validation
- Prompt injection: Mitigated by input/output separation
- Data exfiltration: Mitigated by audit logging
- Model extraction: Mitigated by rate limiting

## Monitoring & Observability

### Three Pillars

**Metrics (Prometheus):**
- Request rate, latency, errors
- Model inference time
- Token usage, costs
- Cache hit rates

**Logs (Structured JSON):**
- Request/response logging
- Error tracking
- Audit events

**Traces (OpenTelemetry):**
- End-to-end request tracing
- Service dependency mapping
- Performance bottleneck identification

## Deployment Architecture

### Production Environment
```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFlare                           │
│                      (CDN + WAF)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│  Kubernetes Cluster     │                                    │
│  ┌──────────────────────┴──────────────────────────────┐    │
│  │              Ingress Controller                      │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│  ┌──────────────────────┼──────────────────────────────┐    │
│  │    ┌─────────┐  ┌─────────┐  ┌─────────┐           │    │
│  │    │ API Pod │  │ API Pod │  │ API Pod │           │    │
│  │    │  (x3)   │  │  (x3)   │  │  (x3)   │           │    │
│  │    └─────────┘  └─────────┘  └─────────┘           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Managed Services                                    │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │ Cloud SQL│ │MemoryStore│ │   GCS   │            │    │
│  │  │(Postgres)│ │ (Redis)  │ │ (Storage)│            │    │
│  │  └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Related Documents

- [AI/ML Strategy](AI_ML_STRATEGY.md)
- [MLOps Practices](MLOPS_PRACTICES.md)
- [Governance Framework](GOVERNANCE.md)
- [Architecture Decision Records](adrs/)
