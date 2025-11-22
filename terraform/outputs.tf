output "backend_url" {
  description = "Backend service URL"
  value       = "https://${render_web_service.backend.service_url}"
}

output "frontend_url" {
  description = "Frontend static site URL"
  value       = "https://${render_static_site.frontend.service_url}"
}

output "backend_service_id" {
  description = "Backend service ID (for GitHub secrets)"
  value       = render_web_service.backend.id
  sensitive   = true
}

output "frontend_service_id" {
  description = "Frontend service ID (for GitHub secrets)"
  value       = render_static_site.frontend.id
  sensitive   = true
}

output "health_check_url" {
  description = "Backend health check endpoint"
  value       = "https://${render_web_service.backend.service_url}/api/v1/health"
}
