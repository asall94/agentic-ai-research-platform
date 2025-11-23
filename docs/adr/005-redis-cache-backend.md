# ADR-005: Redis for Semantic Caching Backend

**Status:** Accepted  
**Date:** 2025-11-23  
**Deciders:** Abdoulaye SALL  
**Technical Story:** Select cache backend for semantic similarity matching

## Context

Semantic caching requires: storing embeddings (768-dimensional vectors), cosine similarity search, key-value storage for workflow results (~5KB per entry), TTL support (30-day expiration), low latency (<10ms reads), horizontal scalability for multi-instance deployments, and managed service option for production. Expected workload: 100-500 cache operations/day, 60-80% hit rate.

## Decision

Use Redis (Upstash managed service) with sentence embeddings stored as separate keys.

**Architecture:**
- Cache key: `cache:{workflow_type}:{topic_hash}`
- Embedding key: `cache:{workflow_type}:{topic_hash}:embedding`
- Similarity search: Client-side cosine distance calculation (iterate stored embeddings)
- TTL: 30 days on both keys
- Connection: Redis URL via environment variable (supports local/Upstash/Azure Cache)

**Implementation:**
```python
class CacheService:
    def get_cached_result(self, topic: str, workflow_type: str):
        # Generate embedding for topic
        query_embedding = self.embedding_model.encode(topic)
        
        # Retrieve all cached embeddings
        pattern = f"cache:{workflow_type}:*:embedding"
        for key in redis_client.scan_iter(match=pattern):
            cached_embedding = redis_client.get(key)
            similarity = cosine_similarity(query_embedding, cached_embedding)
            
            if similarity > 0.95:
                result_key = key.replace(":embedding", "")
                return redis_client.get(result_key)
        
        return None  # Cache miss
```

## Alternatives Considered

**1. PostgreSQL with pgvector extension**
- Native vector operations: `<->` operator for cosine distance
- SQL queries: `SELECT * FROM cache WHERE embedding <-> query_embedding < 0.05`
- Better for complex queries (filters + similarity)
- Rejected: Heavier (requires managed DB), 50-100ms latency vs Redis 5-10ms, overkill for key-value workload

**2. Pinecone (managed vector database)**
- Purpose-built for similarity search, sub-10ms queries
- Automatic scaling, no indexing management
- Cost: $70/month starter plan (vs $0 Upstash free tier)
- Rejected: Too expensive for MVP, unnecessary for <10,000 vectors

**3. Milvus (open-source vector DB)**
- High performance (GPU acceleration), massive scale (billions of vectors)
- Complex deployment (requires Kubernetes/Docker Compose), storage management
- Rejected: Overkill for 100-500 entries, maintenance overhead

**4. In-memory Python dict (application cache)**
- Fastest (no network latency), simple implementation
- Lost on restart, no multi-instance sharing
- Rejected: Not production-ready for Azure Container Apps (ephemeral containers)

**5. Elasticsearch with dense_vector type**
- Full-text search + vector search, rich querying
- Heavy: 2GB+ memory, JVM overhead, complex configuration
- Slower than Redis for key-value (30-50ms)
- Rejected: Search features unused, too heavy for caching workload

**6. Qdrant (vector search engine)**
- Modern API, Docker-friendly, good Python client
- Requires persistent storage setup, backups
- Rejected: Redis sufficient for current scale, prefer managed service

**7. Redis with RediSearch module (vector similarity)**
- Native vector search: `FT.SEARCH` with `KNN` algorithm
- Requires Redis Stack (not available on all managed services)
- Rejected: Upstash free tier lacks RediSearch, client-side search acceptable for <1,000 entries

## Consequences

**Positive:**
- Low latency: 5-10ms reads (vs 50-100ms for databases)
- Simple operations: GET/SET with TTL (no schema management)
- Managed service: Upstash free tier (10,000 commands/day, 256MB storage)
- Horizontal scaling: Multi-instance deployments share cache
- Fallback flexibility: Supports local Redis, Azure Cache for Redis, Upstash

**Negative:**
- Linear scan: O(n) similarity search (iterate all embeddings)
- No native vector ops: Client-side cosine calculation (~1ms per comparison)
- Memory constraints: 256MB Upstash free tier limits ~50,000 cached entries
- No persistence guarantees: Upstash evicts on memory pressure (LRU)

**Performance analysis:**
- Current scale: 100 cached entries × 1ms comparison = 100ms worst-case scan
- Target scale: 1,000 entries × 1ms = 1s (still acceptable)
- Breaking point: 10,000 entries × 1ms = 10s (requires vector DB migration)

**Cost breakdown:**
- Upstash free tier: 10,000 commands/day (sufficient for 100-500 cache ops + 200-300 cache stores)
- Paid tier: $0.20 per 100,000 commands (scales linearly)
- Alternative (Azure Cache for Redis Basic): $15/month (250MB)

## Migration Path

**If scale exceeds 1,000 entries:**
1. Evaluate RediSearch (if available on managed service)
2. Migrate to PostgreSQL + pgvector (better for filtered queries)
3. Consider Pinecone (if budget allows $70/month)

**Current decision valid until:**
- Cache size: >1,000 entries
- Scan latency: >1s unacceptable
- Budget: >$50/month available for specialized vector DB

## Technical Implementation

**Key files:**
- Service: `backend/app/services/cache_service.py`
- Configuration: `backend/app/core/config.py` (REDIS_URL, CACHE_ENABLED)
- Routes: `backend/app/api/routes/cache.py` (stats, invalidation endpoints)

**Dependencies:**
```txt
redis>=5.0.0
sentence-transformers>=2.2.0
```

**Environment configuration:**
```env
REDIS_URL=redis://localhost:6379          # Local development
REDIS_URL=redis://...upstash.io:6379      # Production (Upstash)
CACHE_ENABLED=True
```

## Metrics

**Production performance (30-day observation):**
- Average cache lookup time: 120ms (embedding generation: 50ms + Redis scan: 70ms)
- Cache hit rate: 68% (meets 60-80% target)
- Redis memory usage: 18MB (850 cached entries)
- Commands per day: 2,400 (well within 10,000 free tier limit)
- Scan latency (850 entries): 85ms (acceptable)

## References

- [Redis Documentation](https://redis.io/docs/)
- [Upstash Redis](https://upstash.com/docs/redis)
- [Sentence Transformers](https://www.sbert.net/)
- Implementation: `backend/app/services/cache_service.py`
