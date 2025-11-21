# Semantic Caching Strategy

## Overview
Semantic caching reduces API costs and latency by storing and retrieving similar research queries using embedding similarity instead of exact string matching.

## Why Relevant for This Application
- Workflows cost 3+ OpenAI API calls per execution (45-60s, $0.01-0.05/query)
- Research topics often semantically similar: "AI safety alignment" vs "artificial intelligence safety concerns"
- Academic content stable over weeks (arXiv, Wikipedia change slowly)
- Expected 60-80% cache hit rate for typical usage patterns

## Implementation Decisions

### Cache Scope: Final Reports Only
**Rationale:** Intermediate steps (draft, reflection) are cheap and fast. Final reports are expensive (multiple agent calls) and represent complete value. Caching drafts provides minimal ROI.

### TTL: 30 Days
**Rationale:** Academic research evolves slowly. arXiv papers and Wikipedia articles remain relevant for months. 7 days would be too aggressive (excessive re-computation), 90 days risks stale breaking-news topics. 30 days balances freshness and efficiency.

### Invalidation: Auto (TTL) + Manual Endpoint
**Rationale:** TTL handles 95% of cases automatically. Manual invalidation (`DELETE /api/v1/cache/{hash}`) required for edge cases: correcting bugs, forcing fresh data for updated topics, or full cache flush during debugging.

## Technical Architecture
1. Topic submitted → generate embedding (sentence-transformers)
2. Check Redis for similar embeddings (cosine similarity > 0.95)
3. Cache hit: return stored result immediately
4. Cache miss: execute workflow → store (embedding + result) with 30-day TTL
5. Manual invalidation available via API endpoint

## Expected Impact
- Cost reduction: 60-80% for repeated/similar queries
- Latency improvement: 45s → <500ms for cached results
- No degradation in quality (semantic matching ensures relevance)
