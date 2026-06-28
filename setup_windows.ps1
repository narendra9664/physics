# Setup script for Windows PowerShell
# Run from project root:
#   cd "C:\Users\naren\Desktop\ai-visual-reels"
#   powershell -ExecutionPolicy Bypass -File .\setup_windows.ps1

$ErrorActionPreference = "Stop"

Write-Host "[1/5] Checking Python..." -ForegroundColor Cyan
py --version

Write-Host "[2/5] Checking FFmpeg..." -ForegroundColor Cyan
try {
    ffmpeg -version | Select-Object -First 1
} catch {
    Write-Host "FFmpeg not found on PATH. Install FFmpeg first, then rerun this script." -ForegroundColor Red
    exit 1
}

Write-Host "[3/5] Creating virtual environment..." -ForegroundColor Cyan
if (!(Test-Path ".venv")) {
    py -3.12 -m venv .venv
}

Write-Host "[4/5] Installing Python packages..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "[5/5] Checking Manim..." -ForegroundColor Cyan
.\.venv\Scripts\manim.exe --version

Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next: powershell -ExecutionPolicy Bypass -File .\render_001_embedding.ps1" -ForegroundColor Yellow
