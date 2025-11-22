# Terraform Infrastructure as Code

## Overview

Automates provisioning of Render services for production deployment. Manages backend web service, frontend static site, and environment configuration.

## Prerequisites

**1. Install Terraform:**
```powershell
# Windows (Chocolatey)
choco install terraform

# Or download from: https://www.terraform.io/downloads
```

**2. Get Render API Key:**
```
1. Go to https://dashboard.render.com/
2. Account Settings → API Keys
3. Create new key
4. Copy to environment or tfvars
```

**3. Configure variables:**
```powershell
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
notepad terraform.tfvars
```

## Quick Start

**Using deployment script (recommended):**
```powershell
# 1. Configure secrets
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your API keys

# 2. Initialize
.\deploy.ps1 -Action init

# 3. Preview changes
.\deploy.ps1 -Action plan

# 4. Deploy
.\deploy.ps1 -Action apply

# 5. Get URLs
.\deploy.ps1 -Action output
```

**Manual Terraform commands:**
```powershell
cd terraform
terraform init
terraform plan
terraform apply
terraform output
```

**Destroy infrastructure:**
```powershell
.\deploy.ps1 -Action destroy
# Or: terraform destroy
```

## Deployment Script Features

**`deploy.ps1` provides:**
- Automated validation (checks terraform.tfvars for placeholders)
- Timestamped logs (`terraform-YYYYMMDD-HHMMSS.log`)
- Error handling with exit codes
- Confirmation prompts for destructive operations
- Combined console + file logging

**Actions:**
- `init` - Download Render provider
- `plan` - Preview changes (dry-run)
- `apply` - Create/update infrastructure
- `destroy` - Delete all resources
- `output` - Show deployment URLs

**Example logs:**
```
[2025-11-22 14:30:25] Starting Terraform apply operation
[2025-11-22 14:30:26] terraform.tfvars validation passed
[2025-11-22 14:32:15] Infrastructure deployed successfully
[2025-11-22 14:32:16] Backend URL: https://agentic-ai-backend.onrender.com
```

## Configuration

### terraform.tfvars
```hcl
openai_api_key = "sk-..."
tavily_api_key = "tvly-..."
redis_url      = "redis://upstash-url"
backend_name   = "agentic-backend"
frontend_name  = "agentic-frontend"
region         = "oregon"
```

### Environment Variables (Alternative)
```powershell
$env:TF_VAR_openai_api_key = "sk-..."
$env:TF_VAR_tavily_api_key = "tvly-..."
$env:RENDER_API_KEY = "your-render-api-key"
```

## Resources Created

**Backend Web Service:**
- Free tier Render web service
- Docker runtime with custom Dockerfile
- Auto-deploy from GitHub main branch
- Health checks on `/api/v1/health`
- Environment variables injected

**Frontend Static Site:**
- Free tier static hosting
- React production build
- Auto-deploy from GitHub main branch
- Environment variable for backend URL

## Outputs

After `terraform apply`, you'll get:

```
backend_url         = "https://agentic-ai-backend.onrender.com"
frontend_url        = "https://agentic-ai-frontend.onrender.com"
health_check_url    = "https://agentic-ai-backend.onrender.com/api/v1/health"
backend_service_id  = "srv-xxxxx" (sensitive)
frontend_service_id = "srv-yyyyy" (sensitive)
```

**Use service IDs for GitHub Actions:**
```
Copy backend_service_id → GitHub Secrets → RENDER_BACKEND_SERVICE_ID
Copy frontend_service_id → GitHub Secrets → RENDER_FRONTEND_SERVICE_ID
```

## Workflow

**Initial Deployment:**
```bash
terraform init
terraform plan
terraform apply
# Confirm with 'yes'
```

**Update Configuration:**
```bash
# Edit main.tf or variables
terraform plan  # Preview changes
terraform apply # Apply changes
```

**Check Current State:**
```bash
terraform show
terraform output
```

**Refresh State:**
```bash
terraform refresh
```

## Integration with CI/CD

Terraform creates the infrastructure, GitHub Actions deploys code changes:

```
Developer pushes code
    ↓
GitHub Actions CI/CD
    ↓
Render auto-deploys (via Terraform config)
    ↓
Health checks validate
```

## Best Practices

1. **Never commit terraform.tfvars** (contains secrets)
2. **Use remote state** for team collaboration (S3, Terraform Cloud)
3. **Plan before apply** to review changes
4. **Tag resources** with environment labels
5. **Version lock providers** in providers.tf

## Troubleshooting

**Provider authentication failed:**
```bash
export RENDER_API_KEY=your_key
# Or set in terraform.tfvars: render_api_key = "..."
```

**Service already exists:**
```bash
# Import existing service
terraform import render_web_service.backend srv-xxxxx
```

**State drift detected:**
```bash
# Refresh state to match reality
terraform refresh
terraform plan
```

**Destroy stuck:**
```bash
# Force destroy
terraform destroy -auto-approve
```

## Advanced: Remote State

**Using Terraform Cloud:**
```hcl
terraform {
  backend "remote" {
    organization = "your-org"
    
    workspaces {
      name = "agentic-ai-platform"
    }
  }
}
```

**Using S3:**
```hcl
terraform {
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "agentic-ai/terraform.tfstate"
    region = "us-west-2"
  }
}
```

## Cost Estimation

**All resources on free tier:**
- Backend: $0/month (750 hours free)
- Frontend: $0/month (unlimited static hosting)
- Terraform: $0 (open-source tool)

**Upgrades available:**
- Backend Starter: $7/month (512MB RAM)
- Frontend Pro: $1/month (custom domain + analytics)

## Comparison: Manual vs Terraform

**Manual (Render Dashboard):**
- Click UI to create services
- Copy/paste environment variables
- Manual updates
- No version control

**Terraform (IaC):**
- Code-defined infrastructure
- Version controlled
- Repeatable deployments
- Auditable changes
- Team collaboration
- Multi-environment support

## Next Steps

1. `terraform init` - Download provider
2. `terraform plan` - Preview deployment
3. `terraform apply` - Create infrastructure
4. Copy service IDs to GitHub secrets
5. Push code → Auto-deploy via GitHub Actions
