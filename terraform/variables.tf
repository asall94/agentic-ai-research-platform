variable "render_api_key" {
  description = "Render API key for authentication"
  type        = string
  sensitive   = true
  default     = ""
}

variable "openai_api_key" {
  description = "OpenAI API key for LLM access"
  type        = string
  sensitive   = true
}

variable "tavily_api_key" {
  description = "Tavily API key for web search"
  type        = string
  sensitive   = true
  default     = ""
}

variable "redis_url" {
  description = "Redis connection URL (Upstash)"
  type        = string
  sensitive   = true
  default     = "redis://localhost:6379"
}

variable "backend_name" {
  description = "Name for backend service"
  type        = string
  default     = "agentic-ai-backend"
}

variable "frontend_name" {
  description = "Name for frontend service"
  type        = string
  default     = "agentic-ai-frontend"
}

variable "region" {
  description = "Render deployment region"
  type        = string
  default     = "oregon"
  # Options: oregon, frankfurt, singapore, ohio
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}
