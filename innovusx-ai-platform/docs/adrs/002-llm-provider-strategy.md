# ADR 002: LLM Provider Strategy

## Status
Accepted

## Context
We need to select LLM providers and define a strategy for model selection, fallback, and cost management. Key considerations:
- Response quality for business strategy generation
- Latency requirements (< 3s P99)
- Cost optimization
- Reliability and availability
- Vendor independence

## Decision
We will implement a **multi-provider LLM gateway** with intelligent routing and automatic fallback.

### Primary Configuration
| Use Case | Primary | Fallback 1 | Fallback 2 |
|----------|---------|------------|------------|
| Strategy Generation | GPT-4 Turbo | Claude 3 Sonnet | GPT-3.5 Turbo |
| Embeddings | text-embedding-3-small | - | - |
| Quality Evaluation | GPT-4 | Claude 3 | - |
| Safety Check | Claude 3 | GPT-4 | - |

### Routing Logic
```python
def select_model(request: Request) -> ModelConfig:
    # 1. Check for explicit model override
    if request.model_override:
        return get_model(request.model_override)

    # 2. Route based on request complexity
    complexity = estimate_complexity(request)
    if complexity > 0.8:
        return PRIMARY_MODEL  # GPT-4 for complex requests

    # 3. Route based on cost optimization
    if is_demo_request(request):
        return COST_OPTIMIZED_MODEL  # GPT-3.5 for demos

    # 4. Default to primary
    return PRIMARY_MODEL
```

### Fallback Strategy
```
Attempt 1: Primary model (GPT-4 Turbo)
    ↓ failure or timeout (5s)
Attempt 2: First fallback (Claude 3)
    ↓ failure or timeout (5s)
Attempt 3: Second fallback (GPT-3.5)
    ↓ failure
Return error with graceful degradation message
```

## Alternatives Considered

### Single Provider (OpenAI only)
- **Pros**: Simpler integration, consistent behavior
- **Cons**: Single point of failure, vendor lock-in, no cost optimization
- **Verdict**: Too risky for production

### Open Source Models (Llama, Mistral)
- **Pros**: No API costs, full control, privacy
- **Cons**: Infrastructure burden, lower quality for complex reasoning
- **Verdict**: Consider for future cost optimization, not primary

### Provider Abstraction Layer (LiteLLM)
- **Pros**: Unified API, easy provider switching
- **Cons**: Additional dependency, potential abstraction leakage
- **Verdict**: Use LangChain's built-in abstraction instead

## Consequences

### Positive
- High availability through redundancy
- Cost optimization through intelligent routing
- Vendor independence
- Flexibility to adopt new models

### Negative
- Increased complexity in gateway logic
- Need to maintain multiple API integrations
- Potential inconsistency between model outputs

### Monitoring Requirements
- Track success/failure rates per provider
- Monitor latency percentiles per provider
- Alert on fallback activation
- Track cost per provider

## References
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com)
