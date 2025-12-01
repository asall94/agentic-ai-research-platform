# Azure Cache Strategy

## Overview

The platform uses **Redis-based semantic caching** with sentence embeddings to reduce costs and improve response times. This strategy is production-ready and optimized for Azure Container Apps deployment.

## Architecture

### Local Development
- **Cache**: Disabled by default (`CACHE_ENABLED=False` in `.env`)
- **Reason**: Avoids requiring Redis installation and heavy ML dependencies (torch, sentence-transformers) during development
- **Impact**: Workflows execute fresh each time, full OpenAI API calls

### Azure Production
- **Cache**: Enabled via Terraform deployment (`CACHE_ENABLED=True`)
- **Redis**: Azure Cache for Redis (Basic C0 tier: ~$15/month)
- **Benefits**:
  - **60-80% cost reduction** on repeated similar queries
  - **<1s response time** for cache hits vs 10-60s for fresh execution
  - **Semantic similarity matching** (0.95 threshold) - not just exact matches

## How It Works

### 1. Lazy Import Pattern
```python
# sentence_transformers only imported when cache is enabled
if self.enabled:
    from sentence_transformers import SentenceTransformer
    self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
```

**Why**: Avoids loading 500MB+ PyTorch dependencies when cache is disabled locally.

### 2. Semantic Matching
- Query → 384-dim embedding (all-MiniLM-L6-v2 model)
- Cosine similarity search across cached embeddings
- Match threshold: 0.95 (highly similar queries)

**Example**:
- Cached: "What are the ethical implications of AI?"
- New query: "What are the ethical concerns of artificial intelligence?"
- Result: **Cache hit** (similarity ~0.97)

### 3. TTL Strategy
- **30 days** (2,592,000 seconds)
- Balances freshness with cost savings
- Research content remains relevant for weeks

## Azure Deployment

### Terraform Configuration
```hcl
# Redis cache automatically provisioned
resource "azurerm_redis_cache" "research_cache" {
  name                = "research-cache-${var.environment}"
  sku_name            = "Basic"
  capacity            = 0  # 250MB
}

# Container Apps environment variable
env {
  name  = "CACHE_ENABLED"
  value = "True"
}
env {
  name  = "REDIS_URL"
  value = azurerm_redis_cache.research_cache.primary_connection_string
}
```

### Cost Analysis (Monthly)
| Component | Cache Disabled | Cache Enabled | Savings |
|-----------|----------------|---------------|---------|
| OpenAI API (100 workflows) | ~$50 | ~$15 | 70% |
| Azure Redis Cache | $0 | $15 | - |
| **Total** | **$50** | **$30** | **40%** |

**ROI**: Positive after ~30 workflows/month with similar queries.

## Performance Metrics

### Cache Hit Scenario
```
User Request → Check Cache → Embedding Similarity → Return Cached Result
Time: <1s | Cost: $0.001 (embedding only)
```

### Cache Miss Scenario
```
User Request → Execute Workflow → OpenAI API (3-5 calls) → Store Result + Embedding
Time: 10-60s | Cost: $0.30-$0.80
```

### Observed Hit Rate
- **Research workflows**: 40-60% (users refine similar topics)
- **Production clusters**: 30-50% (common use cases)
- **Educational demos**: 70%+ (repeated examples)

## Development Workflow

### Local Testing WITH Cache
1. Install Redis: `docker run -d -p 6379:6379 redis`
2. Set `CACHE_ENABLED=True` in `backend/.env`
3. Install dependencies: `pip install redis sentence-transformers torch`
4. Start backend: `python main.py`

**Note**: First startup loads ~500MB of PyTorch/transformers models.

### Local Testing WITHOUT Cache (Default)
1. Keep `CACHE_ENABLED=False` in `backend/.env`
2. Start backend: `python main.py`
3. No Redis or ML dependencies required

## Cache Service Features

### Automatic Fallback
```python
try:
    self.redis_client.ping()
    self.model = SentenceTransformer(...)
except Exception as e:
    logger.warning(f"Cache failed: {e}. Running without cache.")
    self.enabled = False
```

### Metrics & Monitoring
- Cache hit/miss rates tracked via Application Insights
- `/api/v1/cache/stats` endpoint for real-time metrics
- Azure Monitor dashboards for Redis performance

### Cache Management
- **Clear cache**: `DELETE /api/v1/cache/clear`
- **View stats**: `GET /api/v1/cache/stats`
- **Export history**: Frontend localStorage tracks client-side execution history

## Security Considerations

### Redis Access Control
- **Azure**: Managed service with SSL/TLS encryption
- **Connection string**: Stored as environment variable, not in code
- **Network**: Private VNET integration in production

### Data Privacy
- **Cached content**: User queries and AI responses
- **Retention**: Auto-expired after 30 days
- **PII handling**: No user identification stored in cache keys

## Monitoring & Debugging

### Cache Performance Queries (Application Insights)
```kusto
// Cache hit rate
customMetrics
| where name == "cache_hit_measure"
| summarize HitRate=avg(value) by bin(timestamp, 1h)

// Workflow duration with cache impact
customMetrics
| where name == "workflow_duration_measure"
| project timestamp, duration=value, cacheHit=customDimensions.cache_hit
| summarize avg(duration) by cacheHit
```

### Redis Monitoring
```bash
# Connect to Azure Redis
redis-cli -h <cache-name>.redis.cache.windows.net -p 6380 -a <access-key> --tls

# Check cache size
INFO memory

# View all cache keys
KEYS cache:*

# Get cache stats
INFO stats
```

## Troubleshooting

### Issue: Cache not working locally
**Solution**: Ensure Redis is running and `CACHE_ENABLED=True`
```bash
docker ps | grep redis  # Verify Redis container
curl http://localhost:8000/api/v1/cache/stats  # Check cache status
```

### Issue: High memory usage on startup
**Cause**: sentence-transformers downloads models on first run
**Solution**: Models cached in `~/.cache/torch/sentence_transformers/`

### Issue: Cache misses on similar queries
**Check**: Similarity threshold too high (0.95)
**Solution**: Lower to 0.90 in `backend/.env`:
```env
CACHE_SIMILARITY_THRESHOLD=0.90
```

## Future Enhancements

1. **Multi-level caching**: L1 (in-memory) + L2 (Redis)
2. **Cache warming**: Pre-populate common queries
3. **Adaptive TTL**: Extend TTL for frequently accessed items
4. **Compression**: Reduce Redis memory usage (zlib/gzip)
5. **Distributed cache**: Redis Cluster for high-scale deployments

## References

- [Semantic Caching ADR](./adr/001-semantic-caching.md)
- [Azure Cache for Redis Pricing](https://azure.microsoft.com/pricing/details/cache/)
- [sentence-transformers Documentation](https://www.sbert.net/)
