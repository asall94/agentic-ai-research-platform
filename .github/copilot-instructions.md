# Copilot Instructions - Agentic AI Research Platform

## Project Overview
Multi-agent research platform implementing three distinct agentic workflows: Simple Reflection (draft→critique→revision), Tool Research (search→reflect→export), and Multi-Agent Orchestration (plan→research→write→edit). Built with FastAPI backend and React frontend.

## Critical Workflow Rule
**NEVER code implementation before explicit user approval.** When user asks for new features:
1. Analyze requirements and propose solution architecture
2. List files to create/modify with brief explanation
3. Wait for user confirmation ("go ahead", "implement", etc.)
4. Only then proceed with code changes

Exception: Bug fixes and direct code correction requests can be implemented immediately.

## Communication Style
**All code, documentation, and scripts must be concise, direct, expertise-oriented, up-to-date on Agentic AI technology, and professional without emojis.**
- Scripts: No decorative emojis in comments, output messages, or logs
- Documentation: Professional technical writing only
- User-facing messages: Clear and formal communication

## Architecture Patterns

### Agent System Design
All agents inherit from `BaseAgent` abstract class (see `backend/app/agents/base_agent.py`):
- **Required:** Override `async def execute(task: str, **kwargs) -> str`
- **Standard params:** `model: str`, `temperature: float = 0.7`
- **Logging:** Use inherited `self.log_execution(task, result)` for consistency
- Seven specialized agents: Draft, Reflection, Revision, Research, Writer, Editor, Planner

### Workflow Pattern (Critical)
Workflows orchestrate agents and return structured dicts, NOT response objects:
```python
# Correct workflow return - dict with specific keys
return {
    "draft": draft_content,
    "reflection": critique,
    "revised": final_output
}
# API routes transform workflow dicts into Pydantic response models
```

### Model Configuration Strategy
Uses prefix-based model naming (`openai:gpt-4o`, `openai:gpt-4o-mini`) configured in `backend/app/core/config.py`:
- **Creative tasks** (drafting, writing): `DEFAULT_DRAFT_MODEL` (gpt-4o) + `temperature=0.7-1.0`
- **Analytical tasks** (planning, reflection): `DEFAULT_REFLECTION_MODEL` (gpt-4o-mini) + `temperature=0.3`
- **Research tasks**: `DEFAULT_RESEARCH_MODEL` (gpt-4o) with tool access
- Override via workflow request parameters: `draft_model`, `reflection_model`, etc.

## Key Technical Decisions

### OpenAI Integration
- Direct `OpenAI()` client usage (NOT aisuite despite being in requirements.txt)
- **Tool calling:** Use `max_turns=6` for iterative tool usage (see `ResearchAgent`)
- **Function definitions:** Tools defined as dicts with OpenAI schema (`arxiv_tool_def` in `backend/app/tools/arxiv_tool.py`)
- **JSON responses:** Prompt for exact JSON format, parse with error handling for markdown-wrapped responses

### Multi-Agent Orchestration (`backend/app/workflows/multi_agent.py`)
1. **Planning:** `PlannerAgent` generates step list
2. **Agent selection:** LLM decides which agent per step via JSON response: `{"agent": "research_agent", "task": "..."}`
3. **Context building:** Previous steps summarized (first 300 chars) and passed to next agent
4. **History tracking:** Each step stores `{step, agent, output}` for final synthesis

### API Response Structure
Routes in `backend/app/api/routes/workflows.py` follow strict pattern:
- Generate unique `workflow_id` via `uuid.uuid4()`
- Track `execution_time` with `time.time()` before/after
- Return workflow-specific Pydantic models (e.g., `ReflectionWorkflowResponse`)
- **Always include error handling** with `status="failed"` and `error` field populated

## Development Workflow

### Running Locally (Windows PowerShell)
```powershell
# Backend (Terminal 1)
cd backend
.\venv\Scripts\activate
python main.py  # Runs uvicorn with reload on localhost:8000

# Frontend (Terminal 2)
cd frontend
npm start  # Runs on localhost:3000
```

### Environment Setup
Required in `backend/.env`:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...  # Free tier: 1000 requests/month
```

### Testing Workflows
```powershell
# Health check
curl http://localhost:8000/api/v1/health

# Reflection workflow
curl -X POST http://localhost:8000/api/v1/workflows/reflection `
  -H "Content-Type: application/json" `
  -d '{"topic": "AI Ethics"}'
```

## Code Conventions

### Logging Standards
- **Backend:** Use module-level `logger = logging.getLogger(__name__)` in every file
- **Log workflow starts:** `logger.info(f"Starting {workflow_name} for: {topic}")`
- **Log step progression:** `logger.info(f"Step {n}: {description}...")`
- **Error logging:** `logger.error(f"{context} error: {e}")` before re-raising

### Error Handling in Tools
Tools return error dicts on failure (see `arxiv_tool.py`):
```python
except Exception as e:
    logger.error(f"arXiv search error: {e}")
    return [{"error": str(e)}]
```

### Frontend API Client (`frontend/src/services/api.js`)
- **Base URL:** `process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'`
- **Timeout:** 300000ms (5 minutes) for long-running workflows
- Service pattern: `workflowService.executeReflectionWorkflow(data)`

## Integration Points

### External APIs
- **arXiv:** Academic papers via `arxiv.Search()` with `SortCriterion.Relevance`
- **Tavily:** Web search requiring API key (configurable `MAX_SEARCH_RESULTS`)
- **Wikipedia:** Encyclopedic content via `wikipedia` package
- All wrapped as OpenAI function calling tools

### CORS Configuration
Defined in `backend/main.py`:
- Origins from `settings.CORS_ORIGINS` env variable (comma-separated)
- Default: `http://localhost:3000,http://localhost:3001`
- Allow all methods and headers for development

## Import Paths
Backend uses absolute imports from `app.*`:
```python
from app.agents import DraftAgent, ReflectionAgent
from app.core.config import settings
from app.workflows.simple_reflection import SimpleReflectionWorkflow
```

## Common Gotchas
1. **Workflow responses:** API routes add metadata (workflow_id, timestamps); workflows return raw dicts
2. **Model prefixes:** Always use `openai:` prefix in config (e.g., `openai:gpt-4o`)
3. **Async patterns:** All agent `execute()` methods and workflow methods are async
4. **JSON parsing:** Multi-agent workflow cleans markdown-wrapped JSON via `_clean_json_block()` regex
5. **Tool execution:** Research agent uses OpenAI's `max_turns` parameter, not manual iteration
