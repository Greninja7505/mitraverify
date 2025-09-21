# PowerShell script to install requirements and run MitraVerify model download
# This script handles the installation issues and Unicode encoding problems

Write-Host "MitraVerify Setup Script" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Set UTF-8 encoding to handle Unicode characters
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

# Set environment variable for UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"

# Navigate to project directory
Set-Location "C:\Users\chira\Desktop\MitraVerify\MitraVerify-Backend"

Write-Host "Step 1: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "Step 2: Installing packages with pre-compiled wheels..." -ForegroundColor Yellow

# Install packages one by one to handle any compilation issues
$packages = @(
    "fastapi==0.115.0",
    "uvicorn[standard]==0.32.0", 
    "python-multipart==0.0.9",
    "numpy==1.26.4",
    "torch==2.6.0",
    "transformers==4.45.0",
    "sentence-transformers==3.1.1",
    "Pillow==11.0.0",
    "pandas==2.2.3",
    "scikit-learn==1.5.2",
    "requests==2.32.3",
    "jinja2==3.1.4",
    "python-dotenv==1.0.1",
    "imagehash==4.3.1",
    "opencv-python==4.10.0.84",
    "matplotlib==3.9.2"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    python -m pip install $package --only-binary=all --no-cache-dir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install $package with binary wheels, trying with compilation..." -ForegroundColor Yellow
        python -m pip install $package --no-cache-dir
    }
}

Write-Host "Step 3: Verifying installation..." -ForegroundColor Yellow
python -c "import transformers, sentence_transformers, torch; print('All packages installed successfully!')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Step 4: Running model download script..." -ForegroundColor Yellow
    python scripts\download_models.py
} else {
    Write-Host "Package verification failed. Please check the installation." -ForegroundColor Red
}

Write-Host "Setup complete!" -ForegroundColor Green