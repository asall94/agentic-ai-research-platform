# Advanced Agentic Research Platform

A comprehensive multi-agent research system with modern web interface, combining reflection patterns, tool usage, and multi-agent orchestration.

## Features

- 🤖 **Multiple Agent Workflows**
  - Simple Reflection (Q2): Draft → Critique → Revision
  - Tool-Enhanced Research (Q3): Search → Reflect → Export
  - Multi-Agent Orchestration (Q5): Planning → Research → Writing → Editing

- 🔧 **Integrated Research Tools**
  - arXiv: Academic papers search
  - Tavily: Web search
  - Wikipedia: Encyclopedia knowledge

- 🎨 **Modern Web Interface**
  - Real-time agent monitoring
  - Interactive workflow configuration
  - Report history and export (HTML/PDF/Markdown)
  - Beautiful, responsive design

## Architecture

```
Projet_Agentic/
├── backend/              # FastAPI server
│   ├── app/
│   │   ├── agents/      # Agent implementations
│   │   ├── tools/       # Research tools
│   │   ├── workflows/   # Workflow orchestrators
│   │   ├── api/         # REST endpoints
│   │   └── models/      # Data models
│   └── main.py
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Application pages
│   │   └── services/    # API clients
│   └── package.json
├── config/
│   └── settings.yaml
└── notebooks/
    └── demo_unified.ipynb
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys:
  - OpenAI API key
  - Tavily API key (free tier: 1000 requests/month)

### Installation

1. **Clone and navigate to project**
```bash
cd "c:\Users\abdsall\Downloads\Research Agent\Projet_Agentic"
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment**
Create `backend/.env`:
```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

4. **Setup Frontend**
```bash
cd ..\frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Access the application at: **http://localhost:3000**

## Usage

### Via Web Interface

1. Navigate to http://localhost:3000
2. Select workflow type (Reflection / Tool-Enhanced / Multi-Agent)
3. Enter your research topic
4. Configure parameters (optional)
5. Click "Start Research"
6. Monitor agents in real-time
7. Export results

### Via API

**Simple Reflection:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/reflection \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI Ethics"}'
```

**Tool-Enhanced Research:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/tool-research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Quantum Computing", "tools": ["arxiv", "wikipedia"]}'
```

**Multi-Agent Workflow:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/multi-agent \
  -H "Content-Type: application/json" \
  -d '{"topic": "Climate Modeling", "max_steps": 4}'
```

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

Edit `config/settings.yaml` to customize:
- Default models (GPT-4, GPT-4o-mini, etc.)
- Temperature settings
- Max tokens
- Tool preferences
- Workflow parameters

## Examples

See `notebooks/demo_unified.ipynb` for comprehensive examples.

## Troubleshooting

**Backend won't start:**
- Verify Python 3.10+ is installed
- Check all dependencies installed: `pip list`
- Ensure .env file exists with valid API keys

**Frontend build errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

**API key errors:**
- Verify keys in `.env` file
- Test keys independently
- Check Tavily free tier limits (1000/month)

## License

MIT License

## Acknowledgments

Based on the Agentic AI course from DeepLearning.AI
