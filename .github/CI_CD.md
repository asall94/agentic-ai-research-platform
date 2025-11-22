# CI/CD Configuration Guide

## GitHub Actions Workflows

### 1. CI Workflow (ci.yml)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

**Backend Tests:**
- Python 3.11 environment
- Installs dependencies from `requirements.txt`
- Runs pytest with coverage
- Uploads coverage to Codecov
- Caches pip dependencies for speed

**Frontend Build:**
- Node.js 18 environment
- Runs `npm ci` for clean install
- Builds production bundle
- Uploads build artifacts
- Caches npm dependencies

**Docker Build:**
- Tests Docker image builds
- Uses BuildKit cache for optimization
- Validates Dockerfiles without pushing

### 2. CD Workflow (deploy.yml)

**Triggers:**
- Push to `main` branch
- Manual trigger via workflow_dispatch

**Jobs:**

**Deploy Backend:**
- Triggers Render deployment via API
- Waits 60s for deployment completion
- Runs health check against `/api/v1/health`

**Deploy Frontend:**
- Runs after backend deployment succeeds
- Triggers Render frontend deployment
- Health checks homepage

**Notify:**
- Reports deployment success/failure
- Logs deployed URLs

## GitHub Secrets Configuration

**Required secrets in repository settings:**

```
OPENAI_API_KEY              # For CI tests
RENDER_API_KEY              # Render account API key
RENDER_BACKEND_SERVICE_ID   # Backend service ID from Render
RENDER_FRONTEND_SERVICE_ID  # Frontend service ID from Render
RENDER_BACKEND_URL          # https://your-backend.onrender.com
RENDER_FRONTEND_URL         # https://your-frontend.onrender.com
```

**Get Render credentials:**
1. Go to https://dashboard.render.com/
2. Account Settings → API Keys → Create new key
3. Each service → Settings → Copy Service ID
4. Add to GitHub: Repository → Settings → Secrets → Actions

## Render Configuration

**Backend Web Service:**
```yaml
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Environment Variables:
  - OPENAI_API_KEY=sk-...
  - TAVILY_API_KEY=tvly-...
  - REDIS_URL=redis://... (from Upstash)
  - CACHE_ENABLED=True
  - LOG_LEVEL=INFO
```

**Frontend Static Site:**
```yaml
Build Command: npm install && npm run build
Publish Directory: build
Environment Variables:
  - REACT_APP_API_URL=https://your-backend.onrender.com/api/v1
```

## Deployment Flow

```
Developer pushes to main
         ↓
CI Workflow runs
  - Backend tests pass
  - Frontend builds successfully
  - Docker images validate
         ↓
CD Workflow triggers
  - Deploy backend to Render
  - Health check backend
  - Deploy frontend to Render
  - Health check frontend
         ↓
Deployment complete
```

## Local Testing

**Test CI locally:**
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend build
cd frontend
npm run build

# Docker build
docker-compose build
```

**Manual deployment:**
```bash
# Trigger via GitHub UI
Actions → CD - Deploy to Render → Run workflow
```

## Monitoring

**Check deployment status:**
- GitHub: Actions tab shows workflow runs
- Render: Dashboard shows deployment logs
- Health: `curl https://your-backend.onrender.com/api/v1/health`

**Rollback on failure:**
- Render auto-keeps previous successful deployment
- Manual rollback: Render Dashboard → Service → Rollback

## Best Practices

1. **Always test locally before pushing to main**
2. **Use pull requests for code review**
3. **Check CI passes before merging**
4. **Monitor deployment health checks**
5. **Keep secrets updated in GitHub settings**

## Troubleshooting

**CI fails on tests:**
- Check logs in Actions tab
- Run tests locally to debug
- Verify dependencies in requirements.txt

**Deployment fails:**
- Check Render build logs
- Verify environment variables set
- Test health endpoint manually

**Health check timeout:**
- Increase wait time in deploy.yml
- Check Render service is running
- Verify URL in secrets is correct
