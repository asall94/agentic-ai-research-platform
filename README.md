# Agentic AI Research Platform

Production-ready multi-agent system for automated research workflows. Built with FastAPI backend and React frontend, implementing advanced agentic patterns including reflection, tool integration, and intelligent orchestration.

## Core Features

**Agent Workflows**
- Simple Reflection: Draft generation, critique, and revision cycle
- Tool-Enhanced Research: Integrated search across arXiv, Tavily, and Wikipedia with automated synthesis
- Multi-Agent Orchestration: Coordinated planning, research, writing, and editing pipeline

**Technical Stack**
- Backend: FastAPI with async support, OpenAI integration, structured logging
- Frontend: React with TailwindCSS, real-time monitoring, responsive design
- Integration: arXiv API, Tavily search, Wikipedia, OpenAI GPT-4/GPT-4o-mini
- Export: HTML, Markdown, JSON formats

## System Architecture

```
backend/
├── app/
│   ├── agents/          # 7 specialized AI agents
│   ├── tools/           # External API integrations
│   ├── workflows/       # Orchestration logic
│   ├── api/routes/      # REST endpoints
│   └── models/          # Pydantic schemas
└── main.py              # FastAPI application

frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Route handlers
│   └── services/        # API client layer
└── package.json
```

## Installation

**Requirements**
- Python 3.10+
- Node.js 18+
- Redis (for semantic caching)
- OpenAI API key
- Tavily API key (optional) 

**Backend Setup**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

**Environment Configuration**
Create `backend/.env`:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
REDIS_URL=redis://localhost:6379
CACHE_ENABLED=True
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
```bash
cd frontend
npm install
```

## Running

**Start Backend** (Terminal 1)
```bash
cd backend
.\venv\Scripts\activate
python main.py
```
Server runs on http://localhost:8000

**Start Frontend** (Terminal 2)
```bash
cd frontend
npm start
```
Application available at http://localhost:3000

## API Usage

**Reflection Workflow**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/reflection \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI Ethics in Healthcare"}'
```

**Research Workflow**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/tool-research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Quantum Computing Applications", "tools": ["arxiv", "wikipedia"]}'
```

**Multi-Agent Workflow**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/multi-agent \
  -H "Content-Type: application/json" \
  -d '{"topic": "Climate Change Modeling", "max_steps": 4}'
```

**API Documentation**
- Interactive docs: http://localhost:8000/docs
- Alternative view: http://localhost:8000/redoc

**Cache Management**
```bash
# Get cache statistics
curl http://localhost:8000/api/v1/cache/stats

# Invalidate all cache
curl -X DELETE http://localhost:8000/api/v1/cache/

# Disable cache (set in .env)
CACHE_ENABLED=False
```

## Semantic Caching

The platform includes intelligent semantic caching to reduce costs and latency:
- Reduces API costs by 60-80% for similar queries
- Improves response time from 45s to <500ms for cached results
- Uses sentence embeddings for semantic similarity matching (threshold: 0.95)
- 30-day TTL for cached results
- See `SEMANTIC_CACHING.md` for details

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
```

## License

Proprietary License - Copyright (c) 2025 Abdoulaye Sall. All rights reserved.

See LICENSE file for details.
