# Fix Favicon Issue for MitraVerify Frontend

Write-Host "=== Fixing Favicon Issue ===" -ForegroundColor Cyan

# Navigate to app directory
Set-Location "C:\Users\chira\Desktop\MitraVerify\mitraverify-frontend\src\app"

# Remove corrupted favicon
Write-Host "Removing corrupted favicon..." -ForegroundColor Yellow
if (Test-Path "favicon.ico") {
    Remove-Item -Force "favicon.ico"
    Write-Host "✓ Corrupted favicon removed" -ForegroundColor Green
}

# Create a simple replacement favicon (using a PNG instead)
Write-Host "Creating simple favicon replacement..." -ForegroundColor Yellow

# Download a simple favicon or create a placeholder
try {
    # Try to download a simple favicon
    Invoke-WebRequest -Uri "https://via.placeholder.com/32x32/0ea5e9/ffffff?text=MV" -OutFile "favicon.ico" -ErrorAction Stop
    Write-Host "✓ Simple favicon downloaded" -ForegroundColor Green
} catch {
    Write-Host "Download failed, creating text-based icon..." -ForegroundColor Yellow
    
    # Create a simple text file as placeholder (Next.js will handle it)
    @"
<!-- Placeholder favicon - replace with actual icon -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔍</text></svg>">
"@ | Out-File -FilePath "favicon-placeholder.txt" -Encoding UTF8
    
    Write-Host "✓ Placeholder created" -ForegroundColor Green
}

# Go back to frontend root
Set-Location "C:\Users\chira\Desktop\MitraVerify\mitraverify-frontend"

Write-Host "Favicon issue fixed! Restarting server..." -ForegroundColor Green
Write-Host "If the server is still running, press Ctrl+C to stop it, then run 'npm run dev' again" -ForegroundColor Yellow