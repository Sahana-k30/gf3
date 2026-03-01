# Quick start script for GF(3) LDPC Error Correction System on Windows (PowerShell)

Write-Host "========================================"
Write-Host "GF(3) LDPC Error Correction System"
Write-Host "========================================"
Write-Host ""

# Check if Python is installed
try {
    python --version 2>&1 | Out-Null
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/"
    Pause
    Exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# Run the backend
Write-Host ""
Write-Host "========================================"
Write-Host "Starting FastAPI Backend Server"
Write-Host "========================================"
Write-Host ""
Write-Host "Server will be running at: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

python main.py
