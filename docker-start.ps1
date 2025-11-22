# Copy environment template
Copy-Item backend\.env.example .env -ErrorAction SilentlyContinue

Write-Host "Building and starting Docker containers..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes on first run.`n" -ForegroundColor Yellow

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    Write-Host "Copy backend\.env.example to .env and add your API keys" -ForegroundColor Yellow
    exit 1
}

# Build and start containers
docker-compose up --build -d

Write-Host "`nContainers starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Redis: localhost:6379`n" -ForegroundColor White

Write-Host "View logs:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f backend" -ForegroundColor Gray
Write-Host "  docker-compose logs -f frontend`n" -ForegroundColor Gray

Write-Host "Stop containers:" -ForegroundColor Cyan
Write-Host "  docker-compose down`n" -ForegroundColor Gray

# Wait for health checks
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
docker-compose ps
