# Deployment Guide - Agentic AI Research Platform

## Render (Free Deployment)

### 1. Backend Web Service

**Configuration:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  ```
  OPENAI_API_KEY=sk-...
  TAVILY_API_KEY=tvly-...
  CACHE_ENABLED=True
  REDIS_URL=redis://...  # From Upstash
  ```

### 2. Frontend Static Site

**Configuration:**
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `build`
- **Environment Variables:**
  ```
  REACT_APP_API_URL=https://your-backend.onrender.com/api/v1
  ```

### 3. Redis (Upstash Free)

1. Sign up: https://upstash.com
2. Create Redis database (free tier: 10k commands/day)
3. Copy connection URL to backend's `REDIS_URL`

**Cost:** 0€/month (with cold starts after inactivity)

---

## Railway ($5 Credit/Month)

### Deploy with Git

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway init
railway up

# Deploy frontend
cd ../frontend
railway init
railway up
```

**Environment Variables:** Same as Render

**Cost:** 0€ if under $5/month, then pay-as-you-go

---

## Fly.io (3 Free VMs)

### Deploy Backend

```bash
# Install flyctl
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Login
fly auth login

# Launch app
cd backend
fly launch
```

**fly.toml:**
```toml
app = "your-app-name"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"
```

**Cost:** 0€ for 3 VMs (256MB each)

---

## Metrics Access

After deployment, access metrics:

**Local:**
- `http://localhost:8000/api/v1/metrics/summary`

**Production:**
- `https://your-backend.onrender.com/api/v1/metrics/summary`

**Response:**
```json
{
  "total_requests": 42,
  "cache_hit_rate": 65.5,
  "avg_execution_time_seconds": 12.3,
  "total_tokens_used": 45000,
  "total_cost_usd": 0.45,
  "cost_savings_from_cache": 0.29,
  "workflows_by_type": {
    "simple_reflection": 20,
    "tool_research": 15,
    "multi_agent": 7
  }
}
```

---

## Cost Comparison

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Render** | 750h/month | Simple, auto-deploy | 15min cold start |
| **Railway** | $5 credit | Fast, no sleep | Paid after credit |
| **Fly.io** | 3 VMs | Always-on | Config complexity |
| **Upstash Redis** | 10k req/day | Generous free tier | Per-command limits |

**Recommendation:** Render (backend + frontend) + Upstash (Redis) = 100% gratuit

---

## GitHub Actions CI/CD

**Automated deployment on every push to main:**

1. **Setup GitHub Secrets:**
   ```
   Repository Settings → Secrets → Actions → New secret
   
   Required secrets:
   - OPENAI_API_KEY
   - RENDER_API_KEY
   - RENDER_BACKEND_SERVICE_ID
   - RENDER_FRONTEND_SERVICE_ID
   - RENDER_BACKEND_URL
   - RENDER_FRONTEND_URL
   ```

2. **Workflows run automatically:**
   - `ci.yml`: Tests + build on every push/PR
   - `deploy.yml`: Auto-deploy to Render on main push

3. **Monitor deployments:**
   - GitHub Actions tab shows workflow status
   - Render dashboard shows deployment logs

See `.github/CI_CD.md` for detailed configuration.

---

## Terraform Infrastructure as Code

**Automated Render deployment:**

```bash
cd terraform
terraform init
terraform apply
```

**Benefits over manual:**
- Version-controlled infrastructure
- Repeatable deployments
- Multi-environment support
- Auditable changes

**Provisions:**
- Backend web service with Docker
- Frontend static site
- Environment variables injection
- Auto-deploy from GitHub

**Outputs service IDs for GitHub Actions secrets.**

See `terraform/README.md` for complete guide.
