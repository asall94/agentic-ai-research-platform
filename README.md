# Agentic AI Research Platform

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Azure](https://img.shields.io/badge/Azure-Container%20Apps-0078D4.svg)](https://azure.microsoft.com/services/container-apps/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC.svg)](https://www.terraform.io/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

Production-ready multi-agent research platform implementing three specialized workflows: Simple Reflection (draft-critique-revise), Tool Research (search-synthesize-export), and Multi-Agent Orchestration (plan-research-write-edit). Built with FastAPI backend, React frontend, deployed on Azure Container Apps with Terraform IaC. Includes semantic caching (60-80% cost reduction), structured JSON logging, rate limiting, and comprehensive CI/CD.

**Live Demo:** https://ca-agentic-ai-frontend.livelydune-8ed54566.westeurope.azurecontainerapps.io

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI<br/>Port 3000]
        NGINX[Nginx<br/>Static Server]
    end
    
    subgraph "API Layer"
        API[FastAPI Backend<br/>Port 8000]
        MIDDLEWARE[Middleware Stack]
        ROUTES[API Routes]
    end
    
    subgraph "Agent System"
        DRAFT[Draft Agent<br/>T=0.7]
        REFLECT[Reflection Agent<br/>T=0.3]
        REVISE[Revision Agent<br/>T=0.5]
        RESEARCH[Research Agent<br/>T=0.3]
        WRITER[Writer Agent<br/>T=0.7]
        EDITOR[Editor Agent<br/>T=0.4]
        PLANNER[Planner Agent<br/>T=0.3]
    end
    
    subgraph "Workflows"
        WF1[Simple Reflection<br/>Draft→Critique→Revise]
        WF2[Tool Research<br/>Search→Synthesize]
        WF3[Multi-Agent<br/>Plan→Execute→Write→Edit]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4o/Mini]
        ARXIV[arXiv API<br/>Academic Papers]
        TAVILY[Tavily API<br/>Web Search]
        WIKI[Wikipedia API<br/>Encyclopedia]
    end
    
    subgraph "Data Layer"
        REDIS[(Redis Cache<br/>Semantic Similarity)]
        METRICS[(Metrics Store<br/>JSON)]
    end
    
    UI --> API
    API --> MIDDLEWARE
    MIDDLEWARE --> |Rate Limit| ROUTES
    MIDDLEWARE --> |Logging| ROUTES
    MIDDLEWARE --> |CORS| ROUTES
    
    ROUTES --> WF1
    ROUTES --> WF2
    ROUTES --> WF3
    
    WF1 --> DRAFT
    WF1 --> REFLECT
    WF1 --> REVISE
    
    WF2 --> RESEARCH
    
    WF3 --> PLANNER
    WF3 --> RESEARCH
    WF3 --> WRITER
    WF3 --> EDITOR
    
    DRAFT --> OPENAI
    REFLECT --> OPENAI
    REVISE --> OPENAI
    RESEARCH --> OPENAI
    RESEARCH --> ARXIV
    RESEARCH --> TAVILY
    RESEARCH --> WIKI
    WRITER --> OPENAI
    EDITOR --> OPENAI
    PLANNER --> OPENAI
    
    API --> REDIS
    API --> METRICS
    
    style UI fill:#61dafb
    style API fill:#009688
    style OPENAI fill:#10a37f
    style REDIS fill:#dc382d
```

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Cache
    participant Workflow
    participant Agent
    participant OpenAI
    participant Metrics

    User->>Frontend: Submit topic
    Frontend->>API: POST /workflows/reflection
    API->>API: Generate correlation_id
    API->>Cache: Check semantic cache
    
    alt Cache Hit
        Cache-->>API: Return cached result
        API->>Metrics: Track (cache_hit=true)
        API-->>Frontend: Return result (< 500ms)
    else Cache Miss
        API->>Workflow: Execute workflow
        Workflow->>Agent: Draft agent
        Agent->>OpenAI: Generate draft
        OpenAI-->>Agent: Draft content
        Workflow->>Agent: Reflection agent
        Agent->>OpenAI: Generate critique
        OpenAI-->>Agent: Critique content
        Workflow->>Agent: Revision agent
        Agent->>OpenAI: Generate revision
        OpenAI-->>Agent: Revised content
        Workflow-->>API: Return result
        API->>Cache: Store with embedding
        API->>Metrics: Track (cache_hit=false)
        API-->>Frontend: Return result (~45s)
    end
    
    Frontend-->>User: Display result
```

## Multi-Agent Orchestration Flow

```mermaid
graph LR
    A[User Request] --> B[Planner Agent]
    B --> C{Generate Steps}
    C --> D[Step 1: Research]
    C --> E[Step 2: Analyze]
    C --> F[Step 3: Write]
    C --> G[Step 4: Edit]
    
    D --> H[LLM Selects<br/>Research Agent]
    E --> I[LLM Selects<br/>Reflection Agent]
    F --> J[LLM Selects<br/>Writer Agent]
    G --> K[LLM Selects<br/>Editor Agent]
    
    H --> L[Context Builder]
    I --> L
    J --> L
    K --> L
    
    L --> M[Final Output]
    
    style B fill:#ffd54f
    style H fill:#81c784
    style I fill:#81c784
    style J fill:#81c784
    style K fill:#81c784
```

## Core Features

**Agent Workflows**
- Simple Reflection: Draft generation, critique, and revision cycle
- Tool-Enhanced Research: Integrated search across arXiv, Tavily, and Wikipedia with automated synthesis
- Multi-Agent Orchestration: Coordinated planning, research, writing, and editing pipeline

**Production-Grade Stack**
- Backend: FastAPI with async support, OpenAI integration, structured logging
- Frontend: React with TailwindCSS, real-time monitoring, responsive design
- Streaming: Server-Sent Events (SSE) for real-time workflow progress (ChatGPT-style UX)
- Cloud: Azure Container Apps with auto-scaling, Application Insights monitoring
- Integration: arXiv API, Tavily search, Wikipedia, OpenAI GPT-4/GPT-4o-mini
- Cache: Redis (Upstash) with semantic similarity matching (60-80% cost reduction)
- Cache-Aware Streaming: Instant results (<1s) on cache hit, progressive updates on miss (60-90s)
- Rate Limiting: 100 requests/15min per IP (configurable)
- DevOps: Docker multi-stage builds, GitHub Actions CI/CD, Terraform IaC (Azure)
- Monitoring: Azure Application Insights with custom metrics (requests, errors, workflows, cache hits)
- Export: HTML, Markdown, JSON formats

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
