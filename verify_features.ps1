# Script de verification des fonctionnalites production

Write-Host "`n=== Verification des fonctionnalites production ===`n" -ForegroundColor Cyan

$results = @()

# 1. Metriques custom
Write-Host "[1/8] Metriques custom..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/metrics/summary" -TimeoutSec 5
    if ($metrics.total_requests -ge 0) {
        Write-Host "  [OK] Metriques fonctionnelles" -ForegroundColor Green
        $results += "[OK] Metriques"
    }
} catch {
    Write-Host "  [KO] Metriques inaccessibles (serveur down?)" -ForegroundColor Red
    $results += "[KO] Metriques"
}

# 2. Rate limiting
Write-Host "[2/8] Rate limiting..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Method GET
    if ($response.Headers.'X-RateLimit-Limit') {
        Write-Host "  [OK] Rate limit actif (limite: $($response.Headers.'X-RateLimit-Limit'))" -ForegroundColor Green
        $results += "[OK] Rate limiting"
    } else {
        Write-Host "  [KO] Headers rate limit manquants" -ForegroundColor Red
        $results += "[KO] Rate limiting"
    }
} catch {
    Write-Host "  [KO] Rate limiting non testable (serveur down?)" -ForegroundColor Red
    $results += "[KO] Rate limiting"
}

# 3. Logs JSON
Write-Host "[3/8] Logs JSON..." -ForegroundColor Yellow
if (Test-Path "backend/app/core/logging_config.py") {
    $logConfig = Get-Content "backend/app/core/logging_config.py" -Raw
    if ($logConfig -match "JSONFormatter") {
        Write-Host "  [OK] JSONFormatter configure" -ForegroundColor Green
        $results += "[OK] Logs JSON"
    } else {
        Write-Host "  [KO] JSONFormatter manquant" -ForegroundColor Red
        $results += "[KO] Logs JSON"
    }
} else {
    Write-Host "  [KO] Fichier logging_config.py manquant" -ForegroundColor Red
    $results += "[KO] Logs JSON"
}

# 4. Docker
Write-Host "[4/8] Docker..." -ForegroundColor Yellow
if ((Test-Path "docker-compose.yml") -and (Test-Path "backend/Dockerfile") -and (Test-Path "frontend/Dockerfile")) {
    Write-Host "  [OK] Fichiers Docker presents" -ForegroundColor Green
    try {
        docker --version | Out-Null
        Write-Host "  [OK] Docker installe" -ForegroundColor Green
        $results += "[OK] Docker"
    } catch {
        Write-Host "  [WARN] Docker non installe" -ForegroundColor Yellow
        $results += "[WARN] Docker"
    }
} else {
    Write-Host "  [KO] Fichiers Docker manquants" -ForegroundColor Red
    $results += "[KO] Docker"
}

# 5. Tests unitaires
Write-Host "[5/8] Tests unitaires..." -ForegroundColor Yellow
if (Test-Path "backend/tests") {
    $testFiles = Get-ChildItem "backend/tests" -Filter "test_*.py"
    if ($testFiles.Count -gt 0) {
        Write-Host "  [OK] $($testFiles.Count) fichiers de tests trouves" -ForegroundColor Green
        $results += "[OK] Tests"
    } else {
        Write-Host "  [KO] Aucun fichier de test" -ForegroundColor Red
        $results += "[KO] Tests"
    }
} else {
    Write-Host "  [KO] Dossier tests/ manquant" -ForegroundColor Red
    $results += "[KO] Tests"
}

# 6. CI/CD
Write-Host "[6/8] CI/CD..." -ForegroundColor Yellow
$ciFiles = @(".github/workflows/ci.yml", ".github/workflows/azure-deploy.yml")
$ciPresent = $true
foreach ($file in $ciFiles) {
    if (-not (Test-Path $file)) {
        $ciPresent = $false
        break
    }
}
if ($ciPresent) {
    Write-Host "  [OK] Workflows GitHub Actions configures" -ForegroundColor Green
    $results += "[OK] CI/CD"
} else {
    Write-Host "  [KO] Workflows manquants" -ForegroundColor Red
    $results += "[KO] CI/CD"
}

# 7. Architecture diagram
Write-Host "[7/8] Architecture diagram..." -ForegroundColor Yellow
if (Test-Path "README.md") {
    $readme = Get-Content "README.md" -Raw
    if ($readme -match "``mermaid") {
        Write-Host "  [OK] Diagrammes Mermaid presents dans README" -ForegroundColor Green
        $results += "[OK] Architecture"
    } else {
        Write-Host "  [KO] Diagrammes manquants" -ForegroundColor Red
        $results += "[KO] Architecture"
    }
} else {
    Write-Host "  [KO] README.md manquant" -ForegroundColor Red
    $results += "[KO] Architecture"
}

# 8. Terraform
Write-Host "[8/8] Terraform..." -ForegroundColor Yellow
if (Test-Path "terraform/main.tf") {
    Write-Host "  [OK] Configuration Terraform presente" -ForegroundColor Green
    try {
        terraform --version | Out-Null
        Write-Host "  [OK] Terraform installe" -ForegroundColor Green
        $results += "[OK] Terraform"
    } catch {
        Write-Host "  [WARN] Terraform non installe" -ForegroundColor Yellow
        $results += "[WARN] Terraform"
    }
} else {
    Write-Host "  [KO] Fichiers Terraform manquants" -ForegroundColor Red
    $results += "[KO] Terraform"
}

# Resume
Write-Host "`n=== Resume ===" -ForegroundColor Cyan
$results | ForEach-Object { Write-Host "  $_" }

$passed = ($results | Where-Object { $_ -like "[OK]*" }).Count
$total = $results.Count
Write-Host "`n$passed/$total fonctionnalites validees" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -lt $total) {
    Write-Host "`nPour tester manuellement:" -ForegroundColor Cyan
    Write-Host "  Backend:  .\start.ps1" -ForegroundColor White
    Write-Host "  Docker:   .\docker-start.ps1" -ForegroundColor White
    Write-Host "  Tests:    .\run_tests.ps1" -ForegroundColor White
}
