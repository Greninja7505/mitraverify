# Complete MitraVerify Startup Script

Write-Host "=== MitraVerify Complete Startup ===" -ForegroundColor Cyan

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

# Step 1: Start Backend
Write-Host "Step 1: Starting Backend..." -ForegroundColor Yellow

if (Test-Port 8000) {
    Write-Host "Backend is already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "Starting backend server..." -ForegroundColor Yellow
    
    # Navigate to backend directory and start server
    Push-Location "MitraVerify-Backend"
    
    # Activate virtual environment if it exists
    if (Test-Path "venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        & "venv\Scripts\Activate.ps1"
    }
    
    # Start backend in background
    Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "src.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Minimized
    
    Pop-Location
    
    # Wait for backend to start
    Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
    $timeout = 30
    $elapsed = 0
    while (-not (Test-Port 8000) -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        Write-Host "." -NoNewline
    }
    Write-Host ""
    
    if (Test-Port 8000) {
        Write-Host "✓ Backend started successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Backend failed to start within $timeout seconds" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Verify Backend Health
Write-Host "Step 2: Verifying Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Backend health check passed" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Start Frontend
Write-Host "Step 3: Starting Frontend..." -ForegroundColor Yellow

if (Test-Port 3000) {
    Write-Host "Frontend is already running on port 3000" -ForegroundColor Green
} else {
    Write-Host "Starting frontend server..." -ForegroundColor Yellow
    
    # Navigate to frontend directory
    Push-Location "mitraverify-frontend"
    
    # Install dependencies if node_modules doesn't exist
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
        npm install --legacy-peer-deps
    }
    
    # Start frontend in background
    Write-Host "Starting Next.js server..." -ForegroundColor Cyan
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized
    
    Pop-Location
    
    # Wait for frontend to start
    Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
    $timeout = 30
    $elapsed = 0
    while (-not (Test-Port 3000) -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 2
        $elapsed += 2
        Write-Host "." -NoNewline
    }
    Write-Host ""
    
    if (Test-Port 3000) {
        Write-Host "✓ Frontend started successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend failed to start within $timeout seconds" -ForegroundColor Red
    }
}

# Step 4: Final Status Check
Write-Host "Step 4: Final Integration Check..." -ForegroundColor Yellow

$backendOk = Test-Port 8000
$frontendOk = Test-Port 3000

Write-Host "`n=== MitraVerify Status ===" -ForegroundColor Cyan
Write-Host "Backend (API): $(if($backendOk){'✓ Running'}else{'✗ Not Running'}) - http://localhost:8000" -ForegroundColor $(if($backendOk){'Green'}else{'Red'})
Write-Host "Frontend (UI): $(if($frontendOk){'✓ Running'}else{'✗ Not Running'}) - http://localhost:3000" -ForegroundColor $(if($frontendOk){'Green'}else{'Red'})

if ($backendOk -and $frontendOk) {
    Write-Host "`n🎉 MitraVerify is fully operational!" -ForegroundColor Green
    Write-Host "`nAccess the application:" -ForegroundColor White
    Write-Host "• Web Interface: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "• API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "• API Health: http://localhost:8000/health" -ForegroundColor Cyan
    
    # Open browser automatically
    $openBrowser = Read-Host "`nOpen web interface in browser? (y/n)"
    if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
        Start-Process "http://localhost:3000"
    }
} else {
    Write-Host "`n⚠️  Setup incomplete. Check the error messages above." -ForegroundColor Yellow
    if (-not $backendOk) {
        Write-Host "Backend troubleshooting:" -ForegroundColor Yellow
        Write-Host "1. Check if Python virtual environment is activated" -ForegroundColor White
        Write-Host "2. Ensure all requirements are installed: pip install -r requirements.txt" -ForegroundColor White
        Write-Host "3. Check logs in MitraVerify-Backend/logs/" -ForegroundColor White
    }
    if (-not $frontendOk) {
        Write-Host "Frontend troubleshooting:" -ForegroundColor Yellow
        Write-Host "1. Ensure Node.js is installed" -ForegroundColor White
        Write-Host "2. Run: npm install --legacy-peer-deps" -ForegroundColor White
        Write-Host "3. Check for port conflicts" -ForegroundColor White
    }
}