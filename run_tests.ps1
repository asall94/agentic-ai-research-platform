# Run all tests
Write-Host "Running unit tests..." -ForegroundColor Cyan

# Activate venv
cd backend
.\venv\Scripts\activate

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
pip install -q pytest pytest-asyncio pytest-cov httpx

# Run tests with coverage
Write-Host "`nExecuting tests...`n" -ForegroundColor Green
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Show coverage summary
Write-Host "`nCoverage report generated in htmlcov/index.html" -ForegroundColor Cyan
Write-Host "Open with: start htmlcov/index.html`n" -ForegroundColor Gray

# Deactivate venv
deactivate
