# Architecture Documentation

## Overview

Multi-agent research platform implementing three agentic workflows with semantic caching, rate limiting, and production-grade observability.

## System Components

### Frontend Layer
- **Technology:** React 18 + TailwindCSS
- **Server:** Nginx (production) or React Dev Server (development)
- **Responsibilities:**
  - User interface for workflow execution
  - Result visualization and export
  - API client with timeout handling (5 min)
  - Responsive design for mobile/desktop

### API Layer
- **Framework:** FastAPI with async support
- **Port:** 8000 (configurable via `API_PORT`)
- **Middleware Stack:**
  1. CORS (configurable origins)
  2. Logging (JSON structured with correlation IDs)
  3. Rate Limiting (100 req/15min per IP)
- **Routes:**
  - `/api/v1/health` - Health check
  - `/api/v1/workflows/*` - Workflow execution
  - `/api/v1/cache/*` - Cache management
  - `/api/v1/metrics/*` - Performance metrics

### Agent System

**Base Architecture:**
- All agents inherit from `BaseAgent` abstract class
- Async execution pattern
- Temperature-controlled creativity
- Structured logging

**7 Specialized Agents:**

| Agent | Purpose | Temperature | Model |
|-------|---------|-------------|-------|
| Draft | Generate initial content | 0.7 | gpt-4o |
| Reflection | Critique and analyze | 0.3 | gpt-4o-mini |
| Revision | Improve based on critique | 0.5 | gpt-4o |
| Research | Search and synthesize | 0.3 | gpt-4o |
| Writer | Create structured content | 0.7 | gpt-4o |
| Editor | Polish and refine | 0.4 | gpt-4o-mini |
| Planner | Decompose tasks into steps | 0.3 | gpt-4o-mini |

### Workflow Orchestration

**Simple Reflection (3 steps):**
```
Topic → Draft Agent → Reflection Agent → Revision Agent → Output
```

**Tool Research:**
```
Topic → Research Agent (with tools) → Synthesized Output
Tools: arXiv, Tavily, Wikipedia
```

**Multi-Agent (4-10 steps):**
```
Topic → Planner Agent → [LLM selects agents per step] → Final Output
Context accumulates across steps (300 char summaries)
```

### Data Layer

**Redis Cache:**
- Semantic similarity matching (cosine similarity ≥ 0.95)
- Embedding model: `all-MiniLM-L6-v2`
- TTL: 30 days
- Key pattern: `cache:{workflow}:{topic_hash}`
- Graceful degradation if unavailable

**Metrics Store:**
- JSON file-based storage
- Tracks: latency, tokens, costs, cache hits
- Aggregation for dashboard
- Historical analysis support

### External Integrations

**OpenAI API:**
- Models: GPT-4o, GPT-4o-mini
- Direct client (not aisuite)
- Tool calling for research agent
- Max turns: 6 for iterative tool use

**Research Tools:**
- **arXiv:** Academic papers via `arxiv` package
- **Tavily:** Web search (1000 free req/month)
- **Wikipedia:** Encyclopedic content

## Deployment Architecture

### Development
```
localhost:3000 (Frontend) → localhost:8000 (Backend) → localhost:6379 (Redis)
```

### Production (Render + Upstash)
```
Frontend Static Site (Render)
    ↓ HTTPS
Backend Web Service (Render)
    ↓ Redis URL
Upstash Redis (Cloud)
```

### Docker Compose
```
Frontend Container (Nginx:alpine)
    ↓ Internal network
Backend Container (Python:3.11-slim)
    ↓ Internal network
Redis Container (Redis:7-alpine)
```

## Security Features

1. **Rate Limiting:** IP-based throttling (configurable)
2. **CORS:** Whitelist origins (production: specific domains)
3. **Non-root containers:** Docker security best practice
4. **API key validation:** Startup checks for required secrets
5. **Secrets management:** Environment variables (never hardcoded)

## Observability

**Structured Logging:**
- Format: JSON for machine parsing
- Fields: timestamp, level, logger, correlation_id, workflow_id, client_ip
- Outputs: stdout (Docker logs, CloudWatch, ELK compatible)

**Metrics:**
- Custom business metrics (cache hit rate, workflow latency)
- Cost tracking (tokens × pricing)
- Exportable to Prometheus format

**Health Checks:**
- `/api/v1/health` endpoint
- Docker healthcheck (30s interval)
- Post-deployment validation in CI/CD

## Performance Optimizations

1. **Semantic Caching:** 60-80% cost reduction for similar queries
2. **Docker Multi-stage:** 60% smaller images
3. **Nginx Gzip:** Compressed responses
4. **Static Asset Caching:** 1-year browser cache
5. **Connection Pooling:** Redis connection reuse
6. **Async Workflows:** Non-blocking I/O throughout

## Scalability Considerations

**Current Limitations:**
- In-memory rate limiter (single instance only)
- File-based metrics (not distributed)

**Production Scaling:**
- Rate limiter → Redis-backed (shared state)
- Metrics → PostgreSQL or TimescaleDB
- Multiple backend instances with load balancer
- Horizontal pod autoscaling (Kubernetes)

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | React | 18.2 |
| UI Framework | TailwindCSS | 3.4 |
| Backend | FastAPI | Latest |
| Language | Python | 3.11+ |
| Runtime | Node.js | 18+ |
| Cache | Redis | 7 |
| LLM | OpenAI GPT-4o/Mini | Latest |
| Containers | Docker | Latest |
| CI/CD | GitHub Actions | - |
| Deployment | Render | - |

## File Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/          # 7 agent implementations
│   │   ├── workflows/       # 3 workflow orchestrators
│   │   ├── api/routes/      # REST endpoints
│   │   ├── core/            # Config, logging, startup
│   │   ├── middleware/      # Rate limiting, logging
│   │   ├── services/        # Cache, metrics
│   │   └── tools/           # arXiv, Tavily, Wikipedia
│   ├── tests/               # Pytest suite (>70% coverage)
│   ├── Dockerfile           # Multi-stage production build
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Route handlers
│   │   └── services/        # API client
│   ├── Dockerfile           # Nginx production build
│   └── package.json         # npm dependencies
├── .github/
│   ├── workflows/           # CI/CD automation
│   └── copilot-instructions.md
└── docker-compose.yml       # Local development stack
```

## Data Flow

**Workflow Execution:**
1. User submits topic via frontend
2. API generates correlation ID
3. Middleware: CORS → Logging → Rate limit check
4. Cache: Check semantic similarity
5. If miss: Execute workflow → Call agents → Query LLMs
6. Store result in cache with embedding
7. Track metrics (latency, tokens, cost)
8. Return response with correlation ID header

**Agent Execution:**
1. Receive task + context
2. Construct prompt with temperature
3. Call OpenAI API (or tools if research)
4. Parse response
5. Log execution details
6. Return result to workflow

**Cache Lookup:**
1. Hash topic
2. Retrieve stored embedding
3. Generate query embedding
4. Calculate cosine similarity
5. If ≥0.95: Return cached result
6. Else: Execute workflow
