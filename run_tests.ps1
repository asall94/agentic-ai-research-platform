# Run all tests
param(
    [switch]$E2E,
    [switch]$DeepEval,
    [switch]$All
)

Write-Host "Running tests..." -ForegroundColor Cyan

# Activate venv
cd backend

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Yellow
python -m pip install -q pytest pytest-asyncio pytest-cov httpx

if ($DeepEval -or $All) {
    python -m pip install -q deepeval
}

# Build test command
$testCmd = "python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html"

if ($E2E) {
    Write-Host "`nRunning E2E tests (real API calls)...`n" -ForegroundColor Yellow
    $testCmd += " --e2e"
}

if ($DeepEval) {
    Write-Host "`nRunning DeepEval quality tests...`n" -ForegroundColor Magenta
    $testCmd += " --deepeval"
}

if ($All) {
    Write-Host "`nRunning ALL tests (unit + E2E + DeepEval)...`n" -ForegroundColor Red
    $testCmd += " --e2e --deepeval"
}

# Run tests with coverage
Write-Host "`nExecuting: $testCmd`n" -ForegroundColor Green
Invoke-Expression $testCmd

# Show coverage summary
Write-Host "`nCoverage report: htmlcov/index.html" -ForegroundColor Cyan
Write-Host "Usage: .\run_tests.ps1 [-E2E] [-DeepEval] [-All]`n" -ForegroundColor Gray
