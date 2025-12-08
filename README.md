# Agentic AI Research Platform

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Azure](https://img.shields.io/badge/Azure-Container%20Apps-0078D4.svg)](https://azure.microsoft.com/services/container-apps/)

Production-ready multi-agent research platform with autonomous workflow orchestration. Implements LLM-driven agent routing, semantic caching (60-80% cost reduction), and real-time streaming. Built with FastAPI backend, React frontend, deployed on Azure Container Apps.

**Live Demo:** https://ca-agentic-ai-frontend.livelydune-8ed54566.westeurope.azurecontainerapps.io

## Agentic Workflows

**Simple Reflection** - Iterative draft improvement via self-critique
- DraftAgent (T=0.7) generates initial essay
- ReflectionAgent (T=0.3) provides structured critique
- RevisionAgent (T=0.5) produces refined version
- Use case: Academic writing, content improvement

**Tool-Enhanced Research** - Multi-source synthesis with external APIs
- ResearchAgent orchestrates parallel searches (arXiv, Tavily, Wikipedia)
- OpenAI function calling with max_turns=6 for iterative tool usage
- Automated citation extraction and source verification
- Use case: Literature reviews, technical research

**Multi-Agent Orchestration** - Dynamic task decomposition and routing
- PlannerAgent (T=0.3) breaks request into executable steps
- LLM selects specialized agent per step via JSON response: `{"agent": "research_agent", "task": "..."}`
- Context propagation across agent chain (300-char summaries prevent token overflow)
- WriterAgent/EditorAgent coordinate final synthesis
- Use case: Complex research reports, multi-stage analysis

**Agent Architecture:**
- 7 specialized agents: Draft, Reflection, Revision, Research, Writer, Editor, Planner
- Abstract BaseAgent class with async `execute()` contract
- Temperature tuning per role: creative (0.7), analytical (0.3), editorial (0.5)
- Stateless design with explicit context passing (no shared memory)

## System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        UI[React + TailwindCSS<br/>SSE Streaming]
    end
    
    subgraph "Backend - FastAPI"
        API[API Routes]
        CACHE[Semantic Cache<br/>Redis + Embeddings]
        MIDDLEWARE[Rate Limit + Logging]
    end
    
    subgraph "Agentic Layer"
        WF1[Reflection Workflow<br/>Draft→Critique→Revise]
        WF2[Tool Research<br/>Multi-source Synthesis]
        WF3[Multi-Agent<br/>LLM-Driven Routing]
        
        DRAFT[Draft Agent T=0.7]
        REFLECT[Reflection Agent T=0.3]
        REVISE[Revision Agent T=0.5]
        RESEARCH[Research Agent T=0.3]
        WRITER[Writer Agent T=0.7]
        EDITOR[Editor Agent T=0.4]
        PLANNER[Planner Agent T=0.3]
    end
    
    subgraph "External APIs"
        OPENAI[OpenAI GPT-4o/Mini]
        ARXIV[arXiv Papers]
        TAVILY[Web Search]
        WIKI[Wikipedia]
    end
    
    UI --> MIDDLEWARE
    MIDDLEWARE --> API
    API --> CACHE
    
    API --> WF1 & WF2 & WF3
    
    WF1 --> DRAFT & REFLECT & REVISE
    WF2 --> RESEARCH
    WF3 --> PLANNER & RESEARCH & WRITER & EDITOR
    
    DRAFT & REFLECT & REVISE & WRITER & EDITOR & PLANNER --> OPENAI
    RESEARCH --> OPENAI & ARXIV & TAVILY & WIKI
    
    style UI fill:#61dafb
    style CACHE fill:#dc382d
    style OPENAI fill:#10a37f
```

**Request Flow:**
1. User submits topic → Frontend sends POST /workflows/{type}
2. API generates correlation_id → Check semantic cache (cosine similarity >0.95)
3. **Cache hit:** Return result <500ms | **Cache miss:** Execute workflow 45-90s
4. Workflow orchestrates agents → Agents call OpenAI/external APIs
5. Result stored in cache with embedding → Response streamed via SSE
6. Metrics tracked: execution time, cache hit/miss, agent usage

## Production Features

**Semantic Caching** - 60-80% cost reduction
- Sentence-transformers embeddings (all-MiniLM-L6-v2, 384-dim)
- Redis with cosine similarity threshold 0.95
- 30-day TTL, ~420ms cached query latency
- Production metrics: 68% cache hit rate, $0.0056/query (vs $0.02 uncached)

**Real-Time Streaming** - Server-Sent Events (SSE)
- Progressive workflow updates (start, progress, step_complete, complete, error)
- Cache-aware: instant delivery on hit, live updates on miss
- EventSource API with automatic reconnection
- Headers: `Cache-Control: no-cache`, `X-Accel-Buffering: no`

**Monitoring & Observability**
- Azure Application Insights integration
- Custom metrics: request duration, workflow execution, cache hits, error rates
- Structured JSON logging with correlation IDs
- Distribution buckets: [50-5000]ms requests, [1-300]s workflows

**Rate Limiting & Security**
- 100 requests/15min per IP (Redis-backed sliding window)
- Health endpoints bypass rate limiting
- CORS configured for production domains
- Input validation: topic 1-500 chars, whitespace trimming

**DevOps & Deployment**
- Docker multi-stage builds (backend 180MB, frontend 25MB)
- GitHub Actions CI/CD with Azure Container Registry
- Terraform IaC for Azure Container Apps (auto-scaling 0-2 replicas)
- Environment: Python 3.12, Node 18, Redis 7

## Quick Start

**With Docker (Recommended):**
```powershell
.\docker-start.ps1
```
Access at http://localhost:3000

**Manual Setup:**
```powershell
# Backend
cd backend
.\venv\Scripts\activate
python main.py

# Frontend (new terminal)
cd frontend
npm start
```

See [Installation](#installation) for detailed setup.

## Project Structure

```
backend/
├── app/
│   ├── agents/          # 7 specialized AI agents
│   ├── api/routes/      # REST endpoints
│   ├── core/            # Config, logging, startup checks
│   ├── middleware/      # Rate limiting, logging middleware
│   ├── models/          # Pydantic schemas
│   ├── services/        # Cache, metrics services
│   ├── tools/           # arXiv, Tavily, Wikipedia integrations
│   └── workflows/       # Orchestration logic
├── tests/               # Pytest suite (>70% coverage)
├── Dockerfile           # Multi-stage production build
└── main.py              # FastAPI application

frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Route handlers
│   └── services/        # API client
├── Dockerfile           # Nginx production build
└── package.json

terraform/               # Infrastructure as Code
.github/workflows/       # CI/CD automation
docker-compose.yml       # Local development stack
```

## Installation

**Requirements**
- Python 3.10+
- Node.js 18+
- Redis (for semantic caching)
- OpenAI API key
- Tavily API key (optional) 

**Backend Setup**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Configuration**
Create `backend/.env`:
```env
# Required
OPENAI_API_KEY=sk-...

# Optional (1000 free searches/month)
TAVILY_API_KEY=tvly-...

# Cache (Upstash Redis free tier)
REDIS_URL=redis://default:password@host.upstash.io:6379
CACHE_ENABLED=True

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=900

# Application Insights (Azure)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
APPINSIGHTS_ENABLED=True
```

**Redis Setup** (Windows)
```powershell
# Install Redis via Chocolatey
choco install redis-64

# Or download from: https://github.com/microsoftarchive/redis/releases
# Start Redis
redis-server
```

**Frontend Setup**
```powershell
cd frontend
npm install
```

## Running

**Option 1: Docker (Recommended)**
```powershell
.\docker-start.ps1
```
All services start automatically: http://localhost:3000

**Option 2: Manual**

**Start Backend** (Terminal 1)
```powershell
cd backend
.\venv\Scripts\activate
python main.py
```
Server runs on http://localhost:8000

**Start Frontend** (Terminal 2)
```powershell
cd frontend
npm start
```
Application available at http://localhost:3000

See `DOCKER.md` for advanced Docker usage.

## API Usage

**Reflection Workflow (Standard)**
```powershell
curl -X POST http://localhost:8000/api/v1/workflows/reflection `
  -H "Content-Type: application/json" `
  -d '{"topic": "AI Ethics in Healthcare"}'
```

**Reflection Workflow (Streaming)**
```powershell
curl -N http://localhost:8000/api/v1/workflows/reflection/stream?topic=AI%20Ethics
# Returns SSE stream with progressive updates
# Event types: start, cache_hit, progress, step_complete, complete, error
```

**Research Workflow (Standard)**
```powershell
curl -X POST http://localhost:8000/api/v1/workflows/tool-research `
  -H "Content-Type: application/json" `
  -d '{"topic": "Quantum Computing Applications", "tools": ["arxiv", "wikipedia"]}'
```

**Research Workflow (Streaming)**
```powershell
curl -N "http://localhost:8000/api/v1/workflows/tool-research/stream?topic=Quantum%20Computing&tools=arxiv,wikipedia"
```

**Multi-Agent Workflow (Standard)**
```powershell
curl -X POST http://localhost:8000/api/v1/workflows/multi-agent `
  -H "Content-Type: application/json" `
  -d '{"topic": "Climate Change Modeling", "max_steps": 4}'
```

**Multi-Agent Workflow (Streaming)**
```powershell
curl -N "http://localhost:8000/api/v1/workflows/multi-agent/stream?topic=Climate%20Change&max_steps=4"
```

**API Documentation**
- Interactive docs: http://localhost:8000/docs
- Alternative view: http://localhost:8000/redoc

**Cache Management**
```powershell
# Get cache statistics
curl http://localhost:8000/api/v1/cache/stats

# Invalidate all cache
curl -X DELETE http://localhost:8000/api/v1/cache/

# Disable cache (set in .env)
CACHE_ENABLED=False
```

## Rate Limiting

**Protection against API abuse:**
- Default: 100 requests per 15 minutes per IP
- Headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- 429 status when exceeded with `Retry-After` header
- Excludes health checks and documentation endpoints

**Test rate limiting:**
```powershell
.\backend\test_rate_limit.ps1
```

**Adjust limits** in `.env`:
```env
RATE_LIMIT_REQUESTS=50      # Stricter for production
RATE_LIMIT_WINDOW_SECONDS=900  # 15 minutes
```

## Real-Time Streaming

Server-Sent Events (SSE) provide ChatGPT-style progressive rendering:
- Progressive UI updates as each agent completes its step
- Cache-aware optimization: <1s instant results on cache hit, 60-90s streaming on miss
- Event types: `start`, `cache_hit`, `progress`, `step_complete`, `complete`, `error`
- Auto-reconnection on network interruption
- Works with Azure Container Apps auto-scaling
- See `docs/adr/006-server-sent-events-streaming.md` for decision rationale

**Frontend Integration:**
```javascript
import { streamWorkflow } from './services/streamingApi';

streamWorkflow('reflection', { topic: 'AI Ethics' }, {
  onProgress: (message) => console.log(message),
  onStepComplete: (step, data) => updateUI(step, data),
  onCacheHit: (data) => showInstantResult(data),
  onComplete: () => finalize(),
  onError: (error) => handleError(error)
});
```

**Performance Metrics**

**Track workflow performance:**
```powershell
curl http://localhost:8000/api/v1/metrics/summary
```

**Response includes:**
- Total requests and cache hit rate
- Average execution time
- Token usage and cost estimates
- Cost savings from caching
- Workflow breakdown by type

Metrics stored in `backend/metrics.json` for historical analysis.

## Application Insights Monitoring

Azure Application Insights provides production telemetry:
- Request duration distribution (cache hit <1s, cache miss 60-90s)
- Error tracking by type with stack traces
- Custom workflow metrics (execution time, cache hit rate)
- Log aggregation with correlation IDs
- Live metrics dashboard in Azure Portal
- Free tier: 5GB/month included with Log Analytics

**Custom Metrics Tracked:**
- `request_duration_ms`: HTTP request latency with distribution buckets [50, 100, 200, 500, 1000, 2000, 5000]ms
- `error_count`: Error count by type and endpoint
- `workflow_duration_seconds`: Workflow execution time with distribution [1, 5, 10, 30, 60, 120, 300]s
- `cache_hit`: Cache hit/miss indicator (1/0)

**Configuration:**
```env
# backend/.env
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
APPINSIGHTS_ENABLED=True
```

**Access logs in Azure Portal:**
1. Navigate to Resource Group → Application Insights resource
2. View Logs, Metrics, Live Metrics, Failures
3. Query with KQL: `requests | where duration > 5000 | summarize count() by resultCode`

## Semantic Caching

Intelligent caching with sentence embeddings reduces costs and latency:
- 60-80% API cost reduction for similar queries
- Response time: 60-90s → <1s for cache hits
- Cosine similarity matching (threshold: 0.95)
- 30-day TTL with manual invalidation endpoint
- Cache-aware streaming: Instant delivery on hit, progressive updates on miss
- See `docs/adr/001-semantic-caching.md` and `docs/adr/006-server-sent-events-streaming.md` for rationale

## Configuration

Configuration via `backend/.env`:
```env
# Models
DEFAULT_DRAFT_MODEL=gpt-4o
DEFAULT_REFLECTION_MODEL=gpt-4o-mini
DEFAULT_RESEARCH_MODEL=gpt-4o

# API Settings
MAX_SEARCH_RESULTS=5
MAX_WORKFLOW_STEPS=4
REQUEST_TIMEOUT=300

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Structured Logging

**JSON logs for production monitoring:**
- Every log entry is valid JSON
- Correlation IDs track requests across services
- Workflow context attached automatically
- Exception tracebacks included

**Log format:**
```json
{
  "timestamp": "2025-11-22T10:30:45Z",
  "level": "INFO",
  "logger": "app.api.routes.workflows",
  "message": "Starting reflection workflow",
  "correlation_id": "abc-123",
  "workflow_id": "workflow-456",
  "client_ip": "127.0.0.1",
  "duration_seconds": 12.5
}
```

**Use cases:**
- Parse with `jq` for filtering: `python main.py | jq 'select(.level=="ERROR")'`
- Export to log aggregators (Datadog, ELK, CloudWatch)
- Alert on error rates or slow requests

**View logs:**
```powershell
.\view_logs.ps1
```

## Testing

**Run unit tests:**
```powershell
.\run_tests.ps1
```

**Test coverage includes:**
- All 7 agents (draft, reflection, revision, research, writer, editor, planner)
- 3 workflows (simple reflection, tool research, multi-agent)
- API endpoints (health, workflows, cache, metrics)
- Middleware (rate limiting, logging)

**Coverage report:** Generated in `backend/htmlcov/index.html`

**Manual testing:**
```powershell
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## CI/CD Pipeline

**Automated deployment via GitHub Actions** (`.github/workflows/azure-deploy.yml`):

**On push to main:**
1. Run pytest with coverage (upload to Codecov)
2. Build Docker images with BuildKit caching
3. Push to Azure Container Registry
4. Deploy to Azure Container Apps
5. Execute health checks (rollback on failure)

**Required GitHub Secrets:**
- `OPENAI_API_KEY` - OpenAI API key for agent execution
- `TAVILY_API_KEY` - Tavily search API key (optional)
- `REDIS_URL` - Redis connection string (Upstash recommended)
- `AZURE_CREDENTIALS` - Azure service principal JSON

Push to `main` branch triggers automatic deployment to Azure.

## Cloud Deployment

**Azure Container Apps** (auto-scaling 0-2 replicas, managed HTTPS, Application Insights, zero-downtime deployments)

**Getting started:**
1. Create Azure account: https://azure.microsoft.com/free
2. Install Azure CLI: `winget install Microsoft.AzureCLI`
3. Login: `az login`
4. Deploy: `cd terraform && .\deploy.ps1 -Action apply`

See `terraform/README.md` for detailed Azure setup guide.

## Infrastructure as Code

**Terraform for Azure Container Apps deployment:**

```powershell
cd terraform

# Initialize Terraform
.\deploy.ps1 -Action init

# Preview infrastructure changes
.\deploy.ps1 -Action plan

# Deploy to Azure
.\deploy.ps1 -Action apply

# Get deployment URLs
.\deploy.ps1 -Action output
```

**Provisions automatically:**
- Resource Group (`rg-agentic-ai-research`)
- Log Analytics Workspace (monitoring)
- Container App Environment
- Azure Container Registry (Docker images)
- Backend Container App (FastAPI)
- Frontend Container App (React)
- All environment variables and secrets

**Cost:** $7.50/month production (free tier: 180,000 vCPU-seconds/month)

**Documentation:** `terraform/README.md` | **Architecture Decisions:** `docs/adr/`

## Author & Copyright

**Abdoulaye SALL** - Lead AI Engineer  
[LinkedIn](https://linkedin.com/in/abdoulaye-sall/) 

**Skills Demonstrated:**
- Multi-agent orchestration with LLM-driven task routing
- Agentic AI workflows (reflection, tool integration, planning)
- Production FastAPI deployment with async patterns
- Server-Sent Events (SSE) for real-time streaming with cache-aware optimization
- Semantic caching with sentence embeddings (60-80% cost reduction)
- OpenAI GPT-4/GPT-4o-mini integration with function calling
- Azure Container Apps deployment with Terraform IaC
- Azure Application Insights monitoring with custom metrics and telemetry
- GitHub Actions CI/CD with automated testing and deployment
- Structured JSON logging for production monitoring
- Rate limiting and middleware architecture
- Redis cache optimization with cosine similarity matching

**License:** Proprietary - See LICENSE for details

**Business Context:** Advanced research platform for automated content generation and synthesis
