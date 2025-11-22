# Docker Deployment Guide

## Quick Start

**Build and run everything:**
```powershell
.\docker-start.ps1
```

Services available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Redis: localhost:6379

## Manual Docker Commands

**Build images:**
```powershell
docker-compose build
```

**Start services:**
```powershell
docker-compose up -d
```

**View logs:**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Stop services:**
```powershell
docker-compose down
```

**Rebuild after code changes:**
```powershell
docker-compose up --build -d
```

## Environment Configuration

Create `.env` in project root:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
CACHE_ENABLED=True
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=900
```

## Production Deployment

**Build for production:**
```powershell
docker-compose -f docker-compose.yml build --no-cache
```

**Push to Azure Container Registry:**
```powershell
# Get ACR name from Terraform output
$ACR_NAME = terraform output -raw container_registry_url

# Login to ACR
az acr login --name acragenticai

# Tag images
docker tag agentic-backend:latest $ACR_NAME/backend:latest
docker tag agentic-frontend:latest $ACR_NAME/frontend:latest

# Push
docker push $ACR_NAME/backend:latest
docker push $ACR_NAME/frontend:latest
```

## Architecture

```
┌─────────────┐
│   Frontend  │  (Nginx + React)
│  Port 3000  │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│   Backend   │  (FastAPI + Python)
│  Port 8000  │
└──────┬──────┘
       │
┌──────▼──────┐
│    Redis    │  (Cache)
│  Port 6379  │
└─────────────┘
```

## Optimization Features

**Backend Dockerfile:**
- Multi-stage build (reduces image size by 60%)
- Non-root user (security)
- Health checks
- Optimized layer caching

**Frontend Dockerfile:**
- Production build with Nginx
- Gzip compression
- Static asset caching (1 year)
- Security headers

**docker-compose.yml:**
- Service dependencies (backend waits for Redis)
- Named volumes (persistent data)
- Health checks for all services
- Auto-restart policies

## Troubleshooting

**Backend won't start:**
```powershell
docker-compose logs backend
# Check API keys in .env
```

**Frontend can't reach backend:**
```powershell
# Verify REACT_APP_API_URL in docker-compose.yml
# Should be http://localhost:8000/api/v1
```

**Redis connection failed:**
```powershell
docker-compose ps redis
# Check Redis health status
```

**Clear everything and restart:**
```powershell
docker-compose down -v
docker-compose up --build -d
```
