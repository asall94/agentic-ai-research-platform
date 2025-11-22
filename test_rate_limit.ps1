# Test rate limiting functionality
Write-Host "Testing Rate Limiting..." -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/v1"
$testRequests = 105  # Exceed limit of 100

Write-Host "`nSending $testRequests requests to test rate limit..." -ForegroundColor Yellow

for ($i = 1; $i -le $testRequests; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -SkipHttpErrorCheck
        
        $remaining = $response.Headers["X-RateLimit-Remaining"]
        $limit = $response.Headers["X-RateLimit-Limit"]
        
        if ($response.StatusCode -eq 429) {
            Write-Host "Request $i - RATE LIMITED (429)" -ForegroundColor Red
            $body = $response.Content | ConvertFrom-Json
            Write-Host "  Error: $($body.error)" -ForegroundColor Red
            Write-Host "  Detail: $($body.detail)" -ForegroundColor Red
            Write-Host "  Retry After: $($body.retry_after) seconds" -ForegroundColor Yellow
            break
        } else {
            if ($i % 10 -eq 0) {
                Write-Host "Request $i - OK (200) | Remaining: $remaining/$limit" -ForegroundColor Green
            }
        }
    }
    catch {
        Write-Host "Request $i - ERROR: $_" -ForegroundColor Red
        break
    }
}

Write-Host "`nRate limiting test completed." -ForegroundColor Cyan
Write-Host "Check that request 101+ returned 429 status." -ForegroundColor Yellow
