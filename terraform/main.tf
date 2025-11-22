resource "render_web_service" "backend" {
  name        = var.backend_name
  plan        = "free"
  region      = var.region
  environment = var.environment

  runtime = "docker"
  
  repo_url = "https://github.com/asall94/agentic-ai-research-platform"
  branch   = "main"
  
  root_directory = "backend"
  dockerfile_path = "Dockerfile"

  # Environment variables
  env_vars = {
    OPENAI_API_KEY              = var.openai_api_key
    TAVILY_API_KEY              = var.tavily_api_key
    REDIS_URL                   = var.redis_url
    CACHE_ENABLED               = "True"
    LOG_LEVEL                   = "INFO"
    RATE_LIMIT_REQUESTS         = "100"
    RATE_LIMIT_WINDOW_SECONDS   = "900"
    APP_NAME                    = "Agentic AI Research Platform"
    DEBUG                       = "False"
  }

  # Health check
  health_check_path = "/api/v1/health"

  # Auto-deploy on push
  auto_deploy = true
}

resource "render_static_site" "frontend" {
  name        = var.frontend_name
  plan        = "free"
  region      = var.region
  environment = var.environment

  repo_url = "https://github.com/asall94/agentic-ai-research-platform"
  branch   = "main"
  
  root_directory = "frontend"
  
  build_command   = "npm install && npm run build"
  publish_path    = "build"

  # Environment variables
  env_vars = {
    REACT_APP_API_URL = "https://${render_web_service.backend.service_url}/api/v1"
  }

  # Auto-deploy on push
  auto_deploy = true
}
