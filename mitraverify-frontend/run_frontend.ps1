# PowerShell script to run MitraVerify Frontend

Write-Host "=== MitraVerify Frontend Setup & Run ===" -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location "C:\Users\chira\Desktop\MitraVerify\mitraverify-frontend"

# Check if Bun is installed
try {
    $bunVersion = bun --version
    Write-Host "Bun version: $bunVersion" -ForegroundColor Green
} catch {
    Write-Host "Bun not found. Installing Bun..." -ForegroundColor Yellow
    
    # Install Bun on Windows
    powershell -c "irm bun.sh/install.ps1 | iex"
    
    # Refresh environment variables
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Host "Bun installed. You may need to restart your terminal." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
bun install

# Check if .env.local exists, if not create a template
if (!(Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    @"
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MitraVerify
"@ | Out-File -FilePath ".env.local" -Encoding UTF8
    Write-Host ".env.local created with default settings" -ForegroundColor Green
}

# Start the development server
Write-Host "Starting Next.js development server..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Make sure the backend is running at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

bun dev