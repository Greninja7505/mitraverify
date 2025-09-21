# Quick Fix Script for MitraVerify Frontend

Write-Host "=== Quick Frontend Fix ===" -ForegroundColor Cyan

# Navigate to frontend directory
Set-Location "C:\Users\chira\Desktop\MitraVerify\mitraverify-frontend"

Write-Host "Step 1: Cleaning npm cache..." -ForegroundColor Yellow
npm cache clean --force

Write-Host "Step 2: Removing node_modules and package-lock.json..." -ForegroundColor Yellow
if (Test-Path "node_modules") { Remove-Item -Recurse -Force "node_modules" }
if (Test-Path "package-lock.json") { Remove-Item -Force "package-lock.json" }

Write-Host "Step 3: Installing with legacy peer deps..." -ForegroundColor Yellow
npm install --legacy-peer-deps

Write-Host "Step 4: Checking if Next.js is available..." -ForegroundColor Yellow
if (Test-Path "node_modules\.bin\next.cmd") {
    Write-Host "✓ Next.js found" -ForegroundColor Green
} else {
    Write-Host "Installing Next.js manually..." -ForegroundColor Yellow
    npm install next@latest --legacy-peer-deps
}

Write-Host "Step 5: Creating .env.local..." -ForegroundColor Yellow
@"
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MitraVerify
"@ | Out-File -FilePath ".env.local" -Encoding UTF8

Write-Host "Setup complete! Now starting server..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan

npm run dev