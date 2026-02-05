# ADR 001: Architecture Style

## Status
Accepted

## Context
We need to decide on the overall architecture style for the InnovusX AI Strategy Lab platform. The system needs to:
- Handle variable load with potential traffic spikes
- Support rapid iteration and deployment
- Enable independent scaling of components
- Maintain high availability
- Support multiple client types (web widget, API clients)

## Decision
We will use a **modular monolith** architecture for the initial implementation, with clear module boundaries that allow future extraction into microservices.

### Structure
```
api/
├── app/
│   ├── main.py           # Single FastAPI application
│   ├── routers/          # HTTP layer (thin)
│   ├── services/         # Business logic modules
│   ├── models/           # Domain models
│   ├── governance/       # Compliance module
│   └── monitoring/       # Observability module
```

### Module Boundaries
- **Strategy Service**: Core business logic for strategy generation
- **RAG Service**: Document retrieval and context building
- **Agent Service**: Multi-agent orchestration
- **LLM Gateway**: Model routing and management
- **Governance**: Audit, PII, access control
- **Monitoring**: Metrics, drift detection

## Alternatives Considered

### Full Microservices
- **Pros**: Independent scaling, technology flexibility
- **Cons**: Operational complexity, network latency, distributed debugging
- **Verdict**: Premature for current scale

### Serverless (Lambda/Cloud Functions)
- **Pros**: Zero infrastructure management, auto-scaling
- **Cons**: Cold starts impact latency, complex state management, vendor lock-in
- **Verdict**: Poor fit for LLM workloads with streaming

### Traditional Monolith
- **Pros**: Simple deployment, easy debugging
- **Cons**: Difficult to scale individual components, tight coupling risk
- **Verdict**: Too rigid for future growth

## Consequences

### Positive
- Single deployment artifact simplifies operations
- In-process communication reduces latency
- Easier debugging and tracing
- Clear path to microservices if needed

### Negative
- Must maintain module discipline to prevent coupling
- Single point of failure (mitigated by horizontal scaling)
- All components scale together (acceptable at current scale)

### Risks
- Module boundaries may erode over time → Mitigate with code reviews and linting
- Performance bottlenecks → Mitigate with profiling and caching

## References
- [Modular Monolith Architecture](https://www.kamilgrzybek.com/design/modular-monolith-primer/)
- [MonolithFirst by Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
