# Terraform Infrastructure as Code

## Overview

Automates provisioning of Azure Container Apps infrastructure for production deployment. Creates Resource Group, Container Registry, Application Insights, Container App Environment with monitoring, and deploys backend/frontend containers.

## Prerequisites

**1. Install Terraform:**
```powershell
# Windows - Direct download
# Download from https://www.terraform.io/downloads
# Extract to C:\Program Files\Terraform
# Add to PATH

# Verify
terraform version
```

**2. Install Azure CLI:**
```powershell
winget install Microsoft.AzureCLI

# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verify
az version
```

**3. Authenticate with Azure:**
```powershell
az login
# Browser opens, sign in with Azure account
```

**4. Configure variables:**
```powershell
# Edit terraform.tfvars with your API keys
notepad terraform\terraform.tfvars
```

## Quick Start

**Using deployment script (recommended):**
```powershell
# 1. Authenticate with Azure
az login

# 2. Configure secrets in terraform.tfvars
notepad terraform\terraform.tfvars
# Set: openai_api_key, tavily_api_key, redis_url

# 3. Initialize
.\terraform\deploy.ps1 -Action init

# 4. Preview changes (7 resources)
.\terraform\deploy.ps1 -Action plan

# 5. Deploy to Azure
.\terraform\deploy.ps1 -Action apply

# 6. Get deployment URLs
.\terraform\deploy.ps1 -Action output
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
.\terraform\deploy.ps1 -Action destroy
# Or: terraform destroy
```

## Deployment Script Features

**`deploy.ps1` provides:**
- Azure CLI authentication validation
- Automated validation (checks terraform.tfvars for placeholders)
- Timestamped logs (`terraform-YYYYMMDD-HHMMSS.log`)
- Error handling with exit codes
- Confirmation prompts for destructive operations
- Combined console + file logging

**Actions:**
- `init` - Download Azure provider
- `plan` - Preview changes (7 resources)
- `apply` - Create/update infrastructure
- `destroy` - Delete all resources
- `output` - Show deployment URLs and ACR credentials

**Example logs:**
```
[2025-11-22 14:30:25] Starting Terraform apply operation
[2025-11-22 14:30:26] terraform.tfvars validation passed
[2025-11-22 14:32:15] Infrastructure deployed successfully
[2025-11-22 14:32:16] Backend URL: https://backend.salmonisland-12345.westeurope.azurecontainerapps.io
```

## Configuration

### terraform.tfvars
```hcl
# Azure subscription ID already set in variables.tf
openai_api_key = "sk-..."
tavily_api_key = "tvly-..."
redis_url      = "redis://default:password@host.upstash.io:6379"
environment    = "production"
```

### Environment Variables (Alternative)
```powershell
$env:TF_VAR_openai_api_key = "sk-..."
$env:TF_VAR_tavily_api_key = "tvly-..."
$env:TF_VAR_redis_url = "redis://..."
```

## Resources Created

Terraform creates 7 Azure resources:

**1. Resource Group** (`rg-agentic-ai-research`)
- Location: West Europe
- Contains all project resources

**2. Log Analytics Workspace**
- 30-day retention
- Powers Application Insights monitoring
- 5GB/month free tier

**3. Application Insights** (`appi-agentic-ai-research-platform`)
- Production telemetry and monitoring
- Custom metrics: request duration, error count, workflow duration, cache hits
- Integrated with Log Analytics workspace
- Free tier: 5GB/month included

**4. Container App Environment**
- Shared runtime for both apps
- Integrated with Log Analytics

**5. Azure Container Registry** (`acragenticai`)
- Basic SKU (free tier eligible)
- Stores backend/frontend Docker images
- Admin credentials enabled

**6. Backend Container App**
- FastAPI application on port 8000
- 0.25 CPU, 0.5Gi memory per replica
- Auto-scaling: 0-2 replicas
- 12 environment variables (API keys, rate limits, Application Insights)
- Health probe: `/api/v1/health`
- External ingress with HTTPS
- Environment variables include: APPLICATIONINSIGHTS_CONNECTION_STRING, APPINSIGHTS_ENABLED

**7. Frontend Container App**
- React application on port 80
- 0.25 CPU, 0.5Gi memory per replica
- Auto-scaling: 0-2 replicas
- REACT_APP_API_URL configured
- External ingress with HTTPS

## Outputs

After `terraform apply`:

```
backend_url                          = "https://backend.salmonisland-12345.westeurope.azurecontainerapps.io"
frontend_url                         = "https://frontend.salmonisland-12345.westeurope.azurecontainerapps.io"
health_check_url                     = "https://backend.../api/v1/health"
resource_group_name                  = "rg-agentic-ai-research"
container_registry_url               = "acragenticai.azurecr.io"
container_registry_username          = "acragenticai" (sensitive)
container_registry_password          = "..." (sensitive)
application_insights_connection_string = "InstrumentationKey=...;IngestionEndpoint=..." (sensitive)
application_insights_instrumentation_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" (sensitive)
```

**Use ACR credentials for CI/CD:**
```powershell
# Get sensitive outputs
terraform output -raw container_registry_password

# Add to GitHub Secrets:
# ACR_USERNAME → container_registry_username
# ACR_PASSWORD → container_registry_password
```

## Workflow

**Initial Deployment:**
```powershell
az login
cd terraform
terraform init
terraform plan  # Review 7 resources to create
terraform apply
# Confirm with 'yes'
```

**Update Configuration:**
```powershell
# Edit main.tf or variables.tf
terraform plan  # Preview changes
terraform apply # Apply changes
```

**Check Current State:**
```powershell
terraform show
terraform output
terraform output -raw container_registry_password
```

**Refresh State:**
```powershell
terraform refresh
```

## Integration with CI/CD

Terraform creates infrastructure, GitHub Actions deploys code updates:

```
Developer pushes code
    ↓
GitHub Actions CI/CD (.github/workflows/deploy.yml)
    ↓
Build Docker images (backend + frontend)
    ↓
Push to Azure Container Registry
    ↓
Update Container Apps with new images
    ↓
Health checks validate deployment
```

**Required GitHub Secrets:**
- `AZURE_CREDENTIALS` (Service Principal JSON)
- `ACR_USERNAME` (from terraform output)
- `ACR_PASSWORD` (from terraform output)

## Best Practices

1. **Never commit terraform.tfvars** (contains secrets, in .gitignore)
2. **Use remote state** for team collaboration (Azure Storage)
3. **Plan before apply** to review changes
4. **Tag resources** with environment/project labels
5. **Lock provider versions** in providers.tf (~> 3.80)
6. **Subscription ID is public** (hardcoded in variables.tf, not sensitive)

## Troubleshooting

**Azure authentication failed:**
```powershell
az login
az account show  # Verify correct subscription
az account set --subscription 9b002981-82da-4e3f-b671-dac15978db4c
```

**Resource already exists:**
```powershell
# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/9b002981-82da-4e3f-b671-dac15978db4c/resourceGroups/rg-agentic-ai-research
```

**State drift detected:**
```powershell
terraform refresh  # Sync state with Azure
terraform plan     # Review differences
```

**Container App deployment fails:**
```powershell
# Check Container App logs
az containerapp logs show --name backend --resource-group rg-agentic-ai-research

# Verify ACR credentials
az acr credential show --name acragenticai
```

**Destroy stuck:**
```powershell
terraform destroy -auto-approve
# Or delete Resource Group manually
az group delete --name rg-agentic-ai-research --yes
```

## Advanced: Remote State

**Using Azure Storage (recommended for teams):**
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstateagentic"
    container_name       = "tfstate"
    key                  = "agentic-ai.tfstate"
  }
}
```

**Setup:**
```powershell
# Create storage for state
az group create --name terraform-state-rg --location westeurope
az storage account create --name tfstateagentic --resource-group terraform-state-rg --sku Standard_LRS
az storage container create --name tfstate --account-name tfstateagentic
```

## Cost Estimation

**Azure Container Apps Free Tier:**
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- First 2 million requests free

**This project usage:**
- Backend: ~0.25 vCPU × 720h = 25,000 vCPU-seconds
- Frontend: ~0.25 vCPU × 720h = 25,000 vCPU-seconds
- **Total: ~50,000 vCPU-seconds/month = 0€ (within free tier)**

**Additional costs:**
- Container Registry (Basic): 0€/month (5GB storage included)
- Log Analytics: 0€/month (5GB/month free tier)
- Application Insights: 0€/month (included with Log Analytics free tier, 5GB/month)
- Upstash Redis: 0€/month (10,000 commands/day free)

**Upgrades available:**
- Dedicated compute: From 4€/month
- Custom domains: Included
- Private networking: VNet integration available

## Comparison: Manual vs Terraform

**Manual (Azure Portal):**
- Click through 6 resource creation wizards
- Copy/paste environment variables manually
- Manual updates and rollbacks
- No version control
- Error-prone configuration

**Terraform (IaC):**
- Code-defined infrastructure (main.tf)
- Version controlled in Git
- Repeatable deployments
- Auditable changes
- Team collaboration
- Multi-environment support (dev/staging/prod)
- One command deployment

## Next Steps

1. **Deploy infrastructure:**
   ```powershell
   az login
   .\terraform\deploy.ps1 -Action init
   .\terraform\deploy.ps1 -Action plan
   .\terraform\deploy.ps1 -Action apply
   ```

2. **Build and push Docker images:**
   ```powershell
   # Get ACR credentials
   $acrPassword = terraform output -raw container_registry_password
   
   # Login to ACR
   docker login acragenticai.azurecr.io -u acragenticai -p $acrPassword
   
   # Build and push backend
   docker build -t acragenticai.azurecr.io/backend:latest ./backend
   docker push acragenticai.azurecr.io/backend:latest
   
   # Build and push frontend
   docker build -t acragenticai.azurecr.io/frontend:latest ./frontend
   docker push acragenticai.azurecr.io/frontend:latest
   ```

3. **Update Container Apps with real images:**
   ```powershell
   # Edit main.tf, replace placeholder images
   # backend: image = "acragenticai.azurecr.io/backend:latest"
   # frontend: image = "acragenticai.azurecr.io/frontend:latest"
   terraform apply
   ```

4. **Configure GitHub Actions CI/CD:**
   - Copy ACR credentials to GitHub Secrets
   - Create `.github/workflows/deploy.yml` for Azure
   - Auto-deploy on push to main

5. **Test deployment:**
   ```powershell
   # Get URLs
   terraform output backend_url
   
   # Test health check
   curl (terraform output -raw health_check_url)
   ```
