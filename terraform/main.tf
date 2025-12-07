# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "Agentic AI Research Platform"
    ManagedBy   = "Terraform"
  }
}

# Log Analytics Workspace (pour Container Apps Environment)
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-${var.project_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = azurerm_resource_group.main.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "appi-${var.project_name}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = azurerm_resource_group.main.tags
}

# Container Apps Environment
resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${var.project_name}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = azurerm_resource_group.main.tags
}

# Container Registry (pour stocker images Docker)
resource "azurerm_container_registry" "main" {
  name                = "acr${replace(var.project_name, "-", "")}${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = azurerm_resource_group.main.tags
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# Backend Container App
resource "azurerm_container_app" "backend" {
  name                         = "ca-${var.project_name}-backend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "backend"
      image  = "docker.io/library/python:3.11-slim"  # Placeholder, will be replaced by CI/CD
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "OPENAI_API_KEY"
        value = var.openai_api_key
      }

      env {
        name  = "TAVILY_API_KEY"
        value = var.tavily_api_key
      }

      env {
        name  = "REDIS_URL"
        value = var.redis_url
      }

      env {
        name  = "CACHE_ENABLED"
        value = "True"
      }

      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }

      env {
        name  = "RATE_LIMIT_REQUESTS"
        value = "100"
      }

      env {
        name  = "RATE_LIMIT_WINDOW_SECONDS"
        value = "900"
      }

      env {
        name  = "APP_NAME"
        value = "Agentic AI Research Platform"
      }

      env {
        name  = "DEBUG"
        value = "False"
      }

      env {
        name  = "PORT"
        value = "8000"
      }

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.main.connection_string
      }

      env {
        name  = "APPINSIGHTS_ENABLED"
        value = "True"
      }

      env {
        name  = "CORS_ORIGINS"
        value = "https://ca-agentic-ai-frontend.livelydune-8ed54566.westeurope.azurecontainerapps.io,http://localhost:3000,http://localhost:3001"
      }
    }

    min_replicas = 1
    max_replicas = 2
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = azurerm_resource_group.main.tags
}

# Frontend Container App
resource "azurerm_container_app" "frontend" {
  name                         = "ca-${var.project_name}-frontend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "frontend"
      image  = "docker.io/library/nginx:alpine"  # Placeholder
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "REACT_APP_API_URL"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}/api/v1"
      }
    }

    min_replicas = 0
    max_replicas = 2
  }

  ingress {
    external_enabled = true
    target_port      = 80
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = azurerm_resource_group.main.tags
}
