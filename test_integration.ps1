# Complete Integration Test Script for MitraVerify

Write-Host "=== MitraVerify Integration Test ===" -ForegroundColor Cyan

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Check if backend is running
Write-Host "Checking backend status..." -ForegroundColor Yellow
if (Test-Port 8000) {
    Write-Host "✓ Backend is running on http://localhost:8000" -ForegroundColor Green
    
    # Test backend health
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Backend health check passed" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Backend health check failed" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Backend is not running on port 8000" -ForegroundColor Red
    Write-Host "Start backend with: cd MitraVerify-Backend && python -m uvicorn src.api.main:app --reload" -ForegroundColor Yellow
}

# Check if frontend is running
Write-Host "Checking frontend status..." -ForegroundColor Yellow
if (Test-Port 3000) {
    Write-Host "✓ Frontend is running on http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "✗ Frontend is not running on port 3000" -ForegroundColor Red
    Write-Host "Start frontend with: cd mitraverify-frontend && npm run dev" -ForegroundColor Yellow
}

# Check environment variables
Write-Host "Checking environment configuration..." -ForegroundColor Yellow
$envFile = "mitraverify-frontend\.env.local"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -match "NEXT_PUBLIC_API_URL=http://localhost:8000") {
        Write-Host "✓ Frontend is configured to use correct backend URL" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend API URL configuration may be incorrect" -ForegroundColor Red
    }
} else {
    Write-Host "! .env.local file not found in frontend" -ForegroundColor Yellow
}

Write-Host "`n=== Integration Test Summary ===" -ForegroundColor Cyan
Write-Host "Backend URL: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend URL: http://localhost:3000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n=== Available API Endpoints ===" -ForegroundColor Cyan
Write-Host "POST /api/v1/verify - Verify text and/or image content" -ForegroundColor White
Write-Host "POST /api/v1/verify/text - Verify text only" -ForegroundColor White
Write-Host "POST /api/v1/verify/image - Verify image only" -ForegroundColor White
Write-Host "GET /api/v1/stats - Get system statistics" -ForegroundColor White
Write-Host "GET /health - Health check" -ForegroundColor White

Write-Host "`n=== Quick Test Commands ===" -ForegroundColor Cyan
Write-Host "Test backend health:" -ForegroundColor Yellow
Write-Host "curl http://localhost:8000/health" -ForegroundColor White
Write-Host "`nTest text verification:" -ForegroundColor Yellow
Write-Host 'curl -X POST http://localhost:8000/api/v1/verify/text -F "text=This is a test message"' -ForegroundColor White

if ((Test-Port 8000) -and (Test-Port 3000)) {
    Write-Host "`n🎉 Integration is ready! Both services are running." -ForegroundColor Green
    Write-Host "Open http://localhost:3000 to test the complete application." -ForegroundColor Green
} else {
    Write-Host "`n⚠️  One or more services are not running. Start them first." -ForegroundColor Yellow
}