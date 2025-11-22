# View JSON logs in real-time
Write-Host "Viewing JSON structured logs (Ctrl+C to stop)..." -ForegroundColor Cyan
Write-Host "Each log entry is a JSON object for parsing/alerting`n" -ForegroundColor Yellow

# Start backend if not running
$backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*backend*" }

if (-not $backendProcess) {
    Write-Host "Backend not running. Starting..." -ForegroundColor Yellow
    cd backend
    .\venv\Scripts\activate
    python main.py
} else {
    Write-Host "Backend running. Monitor logs in terminal or check stdout.`n" -ForegroundColor Green
    Write-Host "Example log entry:" -ForegroundColor Cyan
    Write-Host @"
{
  "timestamp": "2025-11-22T10:30:45.123456Z",
  "level": "INFO",
  "logger": "app.api.routes.workflows",
  "message": "Starting reflection workflow",
  "module": "workflows",
  "function": "execute_reflection_workflow",
  "line": 32,
  "correlation_id": "abc123-def456",
  "workflow_id": "workflow-789",
  "workflow_type": "simple_reflection",
  "client_ip": "127.0.0.1"
}
"@ -ForegroundColor White
    
    Write-Host "`nMake requests to generate logs:" -ForegroundColor Yellow
    Write-Host "curl http://localhost:8000/api/v1/health" -ForegroundColor Gray
}
