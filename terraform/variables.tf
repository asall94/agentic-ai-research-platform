variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "9b002981-82da-4e3f-b671-dac15978db4c"
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "rg-agentic-ai-research"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "project_name" {
  description = "Project name (used for naming resources)"
  type        = string
  default     = "agentic-ai"
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

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "backend_image" {
  description = "Backend Docker image (set by CI/CD)"
  type        = string
  default     = "docker.io/library/python:3.11-slim"
}

variable "frontend_image" {
  description = "Frontend Docker image (set by CI/CD)"
  type        = string
  default     = "docker.io/library/nginx:alpine"
}
