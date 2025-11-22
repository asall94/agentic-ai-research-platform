# Azure CI/CD Setup Guide

## Prerequisites

1. **Azure infrastructure deployed** via Terraform (`terraform apply`)
2. **GitHub repository** with admin access
3. **Azure CLI** installed locally

## Step 1: Create Azure Service Principal

Service Principal allows GitHub Actions to authenticate with Azure.

```powershell
# Login to Azure
az login

# Create Service Principal with Contributor role
az ad sp create-for-rbac `
  --name "github-actions-agentic-ai" `
  --role Contributor `
  --scopes /subscriptions/9b002981-82da-4e3f-b671-dac15978db4c/resourceGroups/rg-agentic-ai-research `
  --sdk-auth
```

**Output example:**
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "9b002981-82da-4e3f-b671-dac15978db4c",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**Copy the entire JSON output** for next step.

## Step 2: Configure GitHub Secrets

Go to: `https://github.com/asall94/agentic-ai-research-platform/settings/secrets/actions`

Add these secrets:

### Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_CREDENTIALS` | Full JSON from Step 1 | Service Principal credentials |
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key for tests |
| `TAVILY_API_KEY` | `tvly-...` | Tavily API key for tests |
| `REDIS_URL` | `redis://...` | Upstash Redis URL for tests |

**How to add:**
1. Click "New repository secret"
2. Name: `AZURE_CREDENTIALS`
3. Value: Paste entire JSON from Step 1
4. Click "Add secret"
5. Repeat for other secrets

## Step 3: Verify Workflow Configuration

Check `.github/workflows/azure-deploy.yml` environment variables:

```yaml
env:
  AZURE_REGISTRY: acragenticai.azurecr.io  # Must match your ACR name
  RESOURCE_GROUP: rg-agentic-ai-research   # Must match Terraform
  BACKEND_APP: backend                      # Must match Terraform
  FRONTEND_APP: frontend                    # Must match Terraform
```

If you changed resource names in Terraform, update these values.

## Step 4: Get Backend URL for Frontend Build

Frontend needs backend URL during build:

```powershell
# Get backend FQDN
az containerapp show `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --query properties.configuration.ingress.fqdn -o tsv
```

**Update workflow** (line 87):
```yaml
--build-arg REACT_APP_API_URL=https://YOUR-BACKEND-FQDN .
```

## Step 5: Test CI/CD

### Trigger deployment:
```powershell
git add .
git commit -m "chore: Configure Azure CI/CD"
git push origin main
```

### Monitor workflow:
1. Go to: `https://github.com/asall94/agentic-ai-research-platform/actions`
2. Click on latest workflow run
3. Watch job progress

### Expected flow:
```
test (2-3 min)
  ├── Install Python dependencies
  ├── Run pytest with coverage
  └── Upload to Codecov

build-and-deploy (5-7 min)
  ├── Azure Login
  ├── Build backend Docker image
  ├── Build frontend Docker image
  ├── Push images to ACR
  ├── Update backend Container App
  ├── Update frontend Container App
  ├── Health check backend
  ├── Health check frontend
  └── Deployment summary
```

## Step 6: Verify Deployment

After successful workflow:

```powershell
# Get deployed URLs
az containerapp show `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --query properties.configuration.ingress.fqdn -o tsv

az containerapp show `
  --name frontend `
  --resource-group rg-agentic-ai-research `
  --query properties.configuration.ingress.fqdn -o tsv
```

Test endpoints:
```powershell
# Backend health check
curl https://YOUR-BACKEND-URL/api/v1/health

# Frontend
curl https://YOUR-FRONTEND-URL
```

## Workflow Triggers

**Automatic deployment:**
- Push to `main` branch → Full CI/CD pipeline
- Pull request → Tests only (no deployment)

**Manual trigger:**
- Go to Actions tab
- Select "Azure Container Apps CI/CD"
- Click "Run workflow"

## Troubleshooting

### Issue: "Error: az: command not found"
**Solution:** GitHub Actions runner has Azure CLI pre-installed. If error persists, check workflow syntax.

### Issue: "Error: Get ACR credentials"
**Solution:** Ensure Service Principal has `AcrPush` role:
```powershell
az role assignment create `
  --assignee <clientId-from-service-principal> `
  --role AcrPush `
  --scope /subscriptions/9b002981-82da-4e3f-b671-dac15978db4c/resourceGroups/rg-agentic-ai-research/providers/Microsoft.ContainerRegistry/registries/acragenticai
```

### Issue: "Container App update failed"
**Solution:** Verify Container Apps exist:
```powershell
az containerapp list --resource-group rg-agentic-ai-research -o table
```

### Issue: "Health check failed"
**Solution:** 
1. Check Container App logs:
```powershell
az containerapp logs show `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --tail 100
```
2. Increase sleep time in workflow (line 109, 123)

### Issue: "Docker build fails"
**Solution:**
1. Test build locally:
```powershell
cd backend
docker build -t test:latest .
```
2. Check Dockerfile syntax
3. Ensure all files in `.dockerignore` are correct

## Rollback Strategy

If deployment introduces issues:

### Option 1: Rollback via Azure Portal
1. Go to Container Apps → backend/frontend
2. Click "Revisions"
3. Activate previous working revision

### Option 2: Rollback via CLI
```powershell
# List revisions
az containerapp revision list `
  --name backend `
  --resource-group rg-agentic-ai-research `
  -o table

# Activate previous revision
az containerapp revision activate `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --revision <previous-revision-name>
```

### Option 3: Redeploy previous image
```powershell
# Find previous commit SHA from GitHub
# Redeploy that image
az containerapp update `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --image acragenticai.azurecr.io/backend:<previous-commit-sha>
```

## Cost Optimization

**Free tier limits:**
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- 2 million requests/month

**Monitor usage:**
```powershell
az monitor metrics list `
  --resource /subscriptions/9b002981-82da-4e3f-b671-dac15978db4c/resourceGroups/rg-agentic-ai-research/providers/Microsoft.App/containerApps/backend `
  --metric "Requests" `
  --start-time 2025-11-01T00:00:00Z `
  --end-time 2025-11-30T23:59:59Z
```

**Scale down when unused:**
```powershell
# Scale to 0 replicas (cost = 0)
az containerapp update `
  --name backend `
  --resource-group rg-agentic-ai-research `
  --min-replicas 0 `
  --max-replicas 0
```

## Next Steps

1. ✅ Configure GitHub Secrets
2. ✅ Update backend URL in workflow
3. ✅ Test first deployment
4. ✅ Monitor logs and metrics
5. ✅ Set up branch protection rules (require CI to pass)
6. ✅ Configure Codecov integration
7. ✅ Add deployment notifications (Slack, email)

## Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
- [Service Principal Best Practices](https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal)
