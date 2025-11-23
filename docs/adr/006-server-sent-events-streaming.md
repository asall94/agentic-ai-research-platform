# ADR-006: Server-Sent Events (SSE) for Real-Time Workflow Progress

**Date:** 2025-11-23  
**Status:** Accepted  
**Context:** Multi-Agent Research Platform - Streaming Implementation

## Context

Workflow execution times (45-90s for multi-agent, 30-60s for reflection) created poor UX with static loading spinners. Users couldn't see progress, didn't know if system was working, and had no feedback on which step was executing. Modern web applications (ChatGPT, Claude, Perplexity) stream responses for better perceived performance.

## Decision

Implement **Server-Sent Events (SSE)** for real-time workflow progress streaming with cache-aware optimization:

### Architecture
- **Backend:** GET endpoints `/workflows/{type}/stream` returning `StreamingResponse`
- **Protocol:** SSE (text/event-stream) with JSON payloads
- **Events:** `start`, `progress`, `step_complete`, `cache_hit`, `complete`, `error`
- **Cache integration:** Check cache before streaming, instant delivery on hit

### Implementation Details
```python
# Backend: streaming.py
async def stream_workflow_progress(workflow_type, topic, workflow_func, cache_service):
    # Check cache first
    cached = cache_service.get_cached_result(topic, workflow_type)
    if cached:
        yield json.dumps({"type": "cache_hit", "data": cached})
        return
    
    # Stream execution + store in cache after completion
    async for event in execute_workflow_with_progress():
        yield event
    cache_service.store_result(topic, workflow_type, result)
```

```javascript
// Frontend: EventSource consumption
const eventSource = new EventSource('/workflows/reflection/stream?topic=...');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Progressive UI updates per event type
};
```

### Event Schema
- **start:** `{"type": "start", "workflow_type": "...", "topic": "..."}`
- **progress:** `{"type": "progress", "step": "draft", "message": "Generating..."}`
- **step_complete:** `{"type": "step_complete", "step": "draft", "data": "..."}`
- **cache_hit:** `{"type": "cache_hit", "data": {...}}` (instant, no streaming)
- **complete:** `{"type": "complete"}`
- **error:** `{"type": "error", "message": "..."}`

## Alternatives Considered

### 1. WebSockets (Bidirectional)
**Rejected:** Overkill for one-way streaming, complex infrastructure (stateful connections, load balancing challenges), higher resource usage.

### 2. Long Polling
**Rejected:** Inefficient (repeated HTTP requests), higher latency, wastes bandwidth, doesn't scale well.

### 3. GraphQL Subscriptions
**Rejected:** Requires GraphQL setup (entire API migration), heavier than SSE, unnecessary complexity for simple streaming.

### 4. HTTP Chunked Transfer
**Rejected:** Non-standard for browser consumption, no built-in reconnection, harder to parse events.

### 5. Polling with Short Intervals
**Rejected:** Database/cache pollution with intermediate results, high latency (500ms-1s delay), inefficient resource usage.

## Consequences

### Positive
- **UX:** ChatGPT-style progressive rendering, users see work happening in real-time
- **Perceived performance:** Feels faster even with same execution time
- **Cache synergy:** Instant results (<1s) on cache hit, streaming on miss (60-90s)
- **Cost efficiency:** Maintains 60-80% cost reduction from semantic caching
- **Simple protocol:** SSE native browser support, auto-reconnection, text-based (easy debugging)
- **Scalable:** Stateless (each stream independent), works with auto-scaling Container Apps

### Negative
- **No IE support:** SSE not supported in Internet Explorer (acceptable in 2025)
- **One-way only:** Can't send data mid-stream (not needed for our use case)
- **Connection limit:** Browser max 6 concurrent SSE per domain (sufficient for single-user workflows)
- **No binary:** Text-only protocol (JSON is text, no issue)

### Risks & Mitigations
- **Risk:** Nginx/proxy buffering breaks streaming  
  **Mitigation:** Added `X-Accel-Buffering: no` header
  
- **Risk:** Cache miss after stream start wastes streaming effort  
  **Mitigation:** Check cache **before** starting stream generator
  
- **Risk:** Network interruption loses progress  
  **Mitigation:** EventSource auto-reconnects, cache stores final result for recovery

## Metrics & Success Criteria

### Performance
- Cache hit: <1s full result delivery (vs 45-90s execution)
- Cache miss: Progressive updates every 15-30s (per agent step)
- Streaming overhead: <100ms per event

### User Experience
- Visibility: Users see plan → step 1 → step 2 → final (not just spinner)
- Feedback: Progress messages explain current action
- Confidence: Real-time updates prove system is working

### Production Validation
- Monitor Application Insights for:
  - Stream connection failures
  - Event parsing errors
  - Cache hit rate with streaming (target: maintain 60-80%)
  - Time to first byte (cache hit should be <500ms)

## References
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [EventSource Browser API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- ADR-001: Semantic Caching (cache integration)
- ADR-002: Multi-Agent Orchestration (workflow steps)

## Implementation
- **Backend:** `backend/app/api/routes/streaming.py` - SSE event generators
- **Backend:** `backend/app/api/routes/workflows.py` - Stream endpoints
- **Frontend:** `frontend/src/services/streamingApi.js` - EventSource client
- **Frontend:** `frontend/src/pages/*Workflow.js` - Progressive UI rendering
- **Deployment:** Azure Container Apps (tested with auto-scaling, no buffering issues)
