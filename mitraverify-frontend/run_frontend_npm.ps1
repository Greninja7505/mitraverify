# Alternative PowerShell script using npm/yarn if Bun is not available

Write-Host "=== MitraVerify Frontend Setup (npm/yarn) ===" -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location "C:\Users\chira\Desktop\MitraVerify\mitraverify-frontend"

# Check if package managers are available
$usePackageManager = $null

if (Get-Command "bun" -ErrorAction SilentlyContinue) {
    $usePackageManager = "bun"
    Write-Host "Using Bun package manager" -ForegroundColor Green
} elseif (Get-Command "yarn" -ErrorAction SilentlyContinue) {
    $usePackageManager = "yarn"
    Write-Host "Using Yarn package manager" -ForegroundColor Green
} elseif (Get-Command "npm" -ErrorAction SilentlyContinue) {
    $usePackageManager = "npm"
    Write-Host "Using npm package manager" -ForegroundColor Green
} else {
    Write-Host "No package manager found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Create .env.local if it doesn't exist
if (!(Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    @"
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MitraVerify
"@ | Out-File -FilePath ".env.local" -Encoding UTF8
    Write-Host ".env.local created" -ForegroundColor Green
}

# Install dependencies based on available package manager
Write-Host "Installing dependencies..." -ForegroundColor Yellow
switch ($usePackageManager) {
    "bun" { bun install }
    "yarn" { yarn install }
    "npm" { 
        # Try normal install first
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Normal install failed, trying with --legacy-peer-deps..." -ForegroundColor Yellow
            npm install --legacy-peer-deps
        }
    }
}

# Check if installation was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency installation failed. Trying alternative approach..." -ForegroundColor Red
    
    # Force install to resolve conflicts
    switch ($usePackageManager) {
        "npm" { 
            Write-Host "Forcing npm install..." -ForegroundColor Yellow
            npm install --force
        }
        "yarn" { 
            Write-Host "Trying yarn with ignore engines..." -ForegroundColor Yellow
            yarn install --ignore-engines
        }
    }
}

# Start development server
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend should be running at: http://localhost:8000" -ForegroundColor Yellow

# Check if Next.js is available before starting
$nextAvailable = $false
switch ($usePackageManager) {
    "bun" { 
        if (Test-Path "node_modules\.bin\next.exe") { $nextAvailable = $true }
    }
    "yarn" { 
        if (Test-Path "node_modules\.bin\next.cmd") { $nextAvailable = $true }
    }
    "npm" { 
        if (Test-Path "node_modules\.bin\next.cmd") { $nextAvailable = $true }
    }
}

if (-not $nextAvailable) {
    Write-Host "Next.js not found. Installing Next.js..." -ForegroundColor Yellow
    switch ($usePackageManager) {
        "bun" { bun add next react react-dom }
        "yarn" { yarn add next react react-dom }
        "npm" { npm install next react react-dom --legacy-peer-deps }
    }
}

switch ($usePackageManager) {
    "bun" { bun dev }
    "yarn" { yarn dev }
    "npm" { npm run dev }
}