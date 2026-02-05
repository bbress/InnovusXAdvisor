# ADR 003: RAG Implementation Strategy

## Status
Accepted

## Context
We need to implement Retrieval-Augmented Generation (RAG) to provide context-aware strategy recommendations. Key decisions include:
- Vector database selection
- Embedding strategy
- Chunking approach
- Retrieval method (dense, sparse, hybrid)
- Reranking strategy

## Decision

### Vector Database: PostgreSQL with pgvector

**Rationale:**
- Already using PostgreSQL for application data
- pgvector provides good performance for our scale (< 100K documents)
- Reduces operational complexity (single database)
- ACID compliance for reliable operations
- Easy backup and recovery

### Embedding Model: OpenAI text-embedding-3-small

**Rationale:**
- 1536 dimensions (good balance of quality and storage)
- Cost-effective ($0.02 per 1M tokens)
- High quality for semantic similarity
- No infrastructure to manage

### Chunking Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                     Chunking Configuration                       │
├─────────────────────────────────────────────────────────────────┤
│  Chunk Size:     512 tokens                                     │
│  Chunk Overlap:  50 tokens (10%)                                │
│  Splitter:       RecursiveCharacterTextSplitter                 │
│  Separators:     ["\n\n", "\n", ". ", " "]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Rationale:**
- 512 tokens balances context richness with retrieval precision
- 10% overlap prevents context loss at boundaries
- Recursive splitter respects document structure

### Retrieval: Hybrid (Dense + Sparse)

```python
def hybrid_search(query: str, k: int = 10) -> list[Document]:
    # Dense search (semantic)
    dense_results = vector_store.similarity_search(
        query_embedding,
        k=k * 2
    )

    # Sparse search (keyword - BM25)
    sparse_results = bm25_index.search(
        query,
        k=k * 2
    )

    # Reciprocal Rank Fusion
    combined = reciprocal_rank_fusion(
        [dense_results, sparse_results],
        k=60  # RRF constant
    )

    return combined[:k]
```

**Rationale:**
- Dense captures semantic similarity
- Sparse captures exact keyword matches
- Hybrid outperforms either alone in benchmarks
- RRF is simple and effective for score fusion

### Reranking: Cross-Encoder

```python
def rerank(query: str, documents: list[Document], k: int = 5) -> list[Document]:
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    pairs = [(query, doc.content) for doc in documents]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:k]]
```

**Rationale:**
- Cross-encoders provide higher accuracy than bi-encoders
- Acceptable latency for top-10 to top-5 reranking (~100ms)
- Significant relevance improvement in benchmarks

## Alternatives Considered

### Vector Database Alternatives

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Pinecone | Managed, scalable | Cost, vendor lock-in | Future consideration |
| Weaviate | Feature-rich, hybrid native | Operational complexity | Overkill for scale |
| Chroma | Simple, embedded | Limited scalability | Too simple |
| Qdrant | Fast, feature-rich | Another service to manage | Good alternative |

### Embedding Alternatives

| Option | Dimensions | Cost | Quality | Verdict |
|--------|------------|------|---------|---------|
| text-embedding-3-large | 3072 | Higher | Better | Future upgrade |
| Cohere embed-v3 | 1024 | Similar | Similar | Good alternative |
| Open source (BGE) | 768 | Free | Good | Self-hosting burden |

## Consequences

### Positive
- Simplified infrastructure (single database)
- Good retrieval quality with hybrid approach
- Cost-effective embedding choice
- Reranking improves final results

### Negative
- pgvector has scalability limits (~1M vectors practical)
- Cross-encoder adds latency
- OpenAI dependency for embeddings

### Migration Path
If we outgrow pgvector:
1. Export embeddings to file
2. Deploy dedicated vector DB (Qdrant/Pinecone)
3. Update retrieval service
4. Keep pgvector as fallback

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Retrieval latency (P50) | < 100ms | Per request |
| Retrieval latency (P99) | < 500ms | Per request |
| Rerank latency | < 150ms | Per request |
| Relevance@5 | > 0.8 | Evaluation set |
| MRR | > 0.7 | Evaluation set |

## References
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Hybrid Search Paper](https://arxiv.org/abs/2210.11934)
- [Cross-Encoder Reranking](https://www.sbert.net/examples/applications/cross-encoder/README.html)
