# Quick Start Guide

## One-Command Launch

```powershell
.\start.ps1
```

Launches both backend (port 8000) and frontend (port 3000). Press Ctrl+C to stop both.

## First-Time Setup

### 1. Install Redis (required for caching)
```powershell
choco install redis-64
redis-server
```

### 2. Install Dependencies

**Backend:**
```powershell
cd backend
pip install -r requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm install
```

### 3. Configure Environment
Copy `backend/.env.example` to `backend/.env` and add your API keys:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://tavily.com (free: 1000 requests/month)

## Manual Launch

**Backend:**
```powershell
cd backend
.\venv\Scripts\activate
python main.py
```

**Frontend:**
```powershell
cd frontend
npm start
```

## Startup Checks

The application automatically verifies:
- Python 3.10+
- Required environment variables (OPENAI_API_KEY)
- Redis connection (if CACHE_ENABLED=True)
- All Python dependencies

Failed checks prevent startup with clear error messages.

## Testing

**Health check:**
```powershell
curl http://localhost:8000/api/v1/health
```

**Reflection workflow:**
```powershell
curl -X POST http://localhost:8000/api/v1/workflows/reflection `
  -H "Content-Type: application/json" `
  -d '{"topic": "AI Ethics"}'
```

## Troubleshooting

**Backend won't start:**
- Check Python 3.10+: `python --version`
- Verify `.env` exists with valid keys
- Review startup check errors in console

**Redis errors:**
- Start Redis: `redis-server`
- Or disable cache: Set `CACHE_ENABLED=False` in `.env`

**Frontend errors:**
```powershell
rm -r node_modules
npm install
```

## Deployment

See README.md for Render deployment instructions.
