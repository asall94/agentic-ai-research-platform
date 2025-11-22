# Railway Deployment Guide

## Setup

**1. Install Railway CLI:**
```powershell
npm install -g @railway/cli
```

**2. Login:**
```powershell
railway login
```

**3. Link project:**
```powershell
railway link
```

## Deploy Backend

```powershell
cd backend
railway up --service backend
```

**Set environment variables:**
```powershell
railway variables set OPENAI_API_KEY=sk-...
railway variables set TAVILY_API_KEY=tvly-...
railway variables set REDIS_URL=redis://...
railway variables set CACHE_ENABLED=True
railway variables set LOG_LEVEL=INFO
railway variables set RATE_LIMIT_REQUESTS=100
railway variables set RATE_LIMIT_WINDOW_SECONDS=900
railway variables set PORT=8000
```

## Deploy Frontend

```powershell
cd ../frontend
railway up --service frontend
railway variables set REACT_APP_API_URL=https://YOUR_BACKEND_URL/api/v1
```

## Get URLs

```powershell
railway domain
```

## Alternative: railway.json Configuration

Create `railway.json` at project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## CI/CD Integration

GitHub Actions with Railway:
```yaml
- name: Deploy to Railway
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
  run: |
    npm install -g @railway/cli
    railway up --service backend
```

## Monitoring

```powershell
railway logs --service backend
railway status
```
