# Unified launcher for Agentic AI Research Platform
# Starts both backend and frontend concurrently

Write-Host "Starting Agentic AI Research Platform..." -ForegroundColor Cyan

# Check if running in correct directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "Error: Must run from project root directory" -ForegroundColor Red
    exit 1
}

# Function to stop all processes on exit
function Stop-Processes {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}

# Register cleanup on Ctrl+C
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Stop-Processes }

try {
    # Start backend
    Write-Host "Starting backend server..." -ForegroundColor Green
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\backend
        .\venv\Scripts\activate
        python main.py
    }

    # Start frontend
    Write-Host "Starting frontend server..." -ForegroundColor Green
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\frontend
        npm start
    }

    Write-Host "`nServers starting..." -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8000" -ForegroundColor White
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "`nPress Ctrl+C to stop all services`n" -ForegroundColor Yellow

    # Monitor jobs and display output
    while ($true) {
        # Check if jobs are still running
        if ($backendJob.State -eq "Failed") {
            Write-Host "Backend crashed!" -ForegroundColor Red
            Receive-Job $backendJob
            break
        }
        if ($frontendJob.State -eq "Failed") {
            Write-Host "Frontend crashed!" -ForegroundColor Red
            Receive-Job $frontendJob
            break
        }

        # Display any output
        Receive-Job $backendJob -ErrorAction SilentlyContinue
        Receive-Job $frontendJob -ErrorAction SilentlyContinue

        Start-Sleep -Seconds 1
    }
}
finally {
    Stop-Processes
    Write-Host "All services stopped" -ForegroundColor Green
}
