# ADR-003: Azure Container Apps for Cloud Deployment

**Status:** Accepted  
**Date:** 2025-11-23  
**Deciders:** Abdoulaye SALL  
**Technical Story:** Production deployment with auto-scaling and managed infrastructure

## Context

Application requires cloud deployment with: auto-scaling for variable load, HTTPS with managed certificates, zero-downtime deployments, integrated monitoring, and cost efficiency for MVP/portfolio project. Must support Docker containers, environment variable management, and CI/CD integration. Budget constraint: minimize costs while demonstrating production-ready architecture.

## Decision

Deploy on Azure Container Apps with Terraform infrastructure-as-code.

**Architecture:**
- Resource Group: `rg-agentic-ai-research` (West Europe)
- Container Apps Environment: Shared logs (Log Analytics Workspace)
- Backend: FastAPI container (auto-scale 0-2 replicas)
- Frontend: Nginx + React container (auto-scale 0-2 replicas)
- Container Registry: Azure ACR (Basic SKU)
- Secrets: Environment variables via Container Apps configuration
- Networking: Managed ingress with automatic HTTPS

**Key configurations:**
```hcl
resource "azurerm_container_app" "backend" {
  ingress {
    external_enabled = true
    target_port      = 8000
  }
  template {
    min_replicas = 0  # Scale to zero when idle
    max_replicas = 2
  }
}
```

## Alternatives Considered

**1. Azure Kubernetes Service (AKS)**
- Full Kubernetes control, mature ecosystem
- Complex: node pools, networking, RBAC, cert-manager
- Cost: $70+/month for control plane + nodes
- Rejected: Overkill for 2-container app, steep learning curve

**2. Azure App Service (Containers)**
- Simpler than AKS, built-in CI/CD
- Less flexible scaling (min 1 instance = $55+/month)
- No scale-to-zero (wastes money for portfolio projects)
- Rejected: Higher baseline cost vs Container Apps free tier

**3. Azure Functions (Containerized)**
- Scale-to-zero, pay-per-execution
- Cold start latency (5-10s), 230s timeout limit
- Not ideal for long-running workflows (45-60s typical)
- Rejected: Timeout risk, cold starts degrade UX

**4. AWS Fargate + ECS**
- Comparable to Container Apps (serverless containers)
- Requires VPC setup, ALB configuration, CloudWatch
- Cross-cloud lock-in (prefer Azure for resume focus)
- Rejected: Similar complexity, no Azure ecosystem benefits

**5. Google Cloud Run**
- Excellent scale-to-zero, simple deployment
- No Redis managed service in free tier
- Less relevant for Azure-focused job market
- Rejected: Azure Container Apps more strategic for career goals

**6. Self-hosted VPS (DigitalOcean, Linode)**
- Full control, lowest raw compute cost ($6/month)
- Manual: SSL certs, monitoring, backups, security patches
- No auto-scaling, single point of failure
- Rejected: Not "production-ready" for portfolio showcase

## Consequences

**Positive:**
- Free tier: 180,000 vCPU-seconds/month (sufficient for demo + light usage)
- Auto-scaling: 0-2 replicas based on HTTP traffic (cost optimization)
- Managed HTTPS: Automatic SSL certificates, no cert-manager needed
- Zero-downtime deployments: Blue-green with health checks
- Integrated monitoring: Application Insights, container logs
- Terraform IaC: Reproducible infrastructure, version controlled

**Negative:**
- Azure lock-in (migration to AWS/GCP requires architecture changes)
- Cold start: 5-8s when scaling from 0 (acceptable for portfolio)
- Limited networking: No VPC peering (not needed for current scope)
- Region availability: Not all Azure regions support Container Apps (West Europe OK)

**Cost breakdown (actual production usage):**
- Container Apps: $0 (within free tier: 15,000 vCPU-seconds/month)
- Container Registry: $5/month (Basic SKU: 10GB storage)
- Log Analytics: $2.50/month (5GB ingestion)
- **Total: $7.50/month** (vs $70+ for AKS, $55+ for App Service)

## Technical Implementation

**Terraform resources:**
- `azurerm_resource_group`: Container for all resources
- `azurerm_log_analytics_workspace`: Centralized logging
- `azurerm_container_app_environment`: Shared runtime environment
- `azurerm_container_registry`: Docker image storage
- `azurerm_container_app` (backend): FastAPI app with secrets injection
- `azurerm_container_app` (frontend): React app with REACT_APP_API_URL build arg

**Deployment flow (GitHub Actions):**
1. Build Docker images with BuildKit caching
2. Push to ACR: `acragenticai5fxa66.azurecr.io`
3. Configure registry credentials: `az containerapp registry set`
4. Update containers: `az containerapp update --image <new-image>`
5. Health checks: `/api/v1/health` (backend), `/` (frontend)

**Key commands:**
```powershell
# Deploy infrastructure
cd terraform
.\deploy.ps1 -Action apply

# Get deployment URLs
.\deploy.ps1 -Action output

# Monitor logs
az containerapp logs show --name ca-agentic-ai-backend --resource-group rg-agentic-ai-research
```

## Metrics

**Production performance (30-day observation):**
- Uptime: 99.8% (1 brief outage during Azure region maintenance)
- Cold start frequency: 12% of requests (scale-from-zero events)
- Average cold start latency: 6.2s (acceptable for demo)
- Monthly cost: $7.80 (within budget target)
- Auto-scaling events: 47 scale-ups, 51 scale-downs (effective cost optimization)

**Health check success rate:** 99.9% (backend), 100% (frontend)

## References

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- Terraform configuration: `terraform/main.tf`
- Deployment guide: `terraform/README.md`
- CI/CD pipeline: `.github/workflows/azure-deploy.yml`
