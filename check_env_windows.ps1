# Environment check for Windows PowerShell
# Run from project root:
#   cd "C:\Users\naren\Desktop\ai-visual-reels"
#   powershell -ExecutionPolicy Bypass -File .\check_env_windows.ps1

Write-Host "Python:" -ForegroundColor Cyan
py --version

Write-Host "FFmpeg:" -ForegroundColor Cyan
try { ffmpeg -version | Select-Object -First 1 } catch { Write-Host "Not found" -ForegroundColor Red }

Write-Host "Project venv:" -ForegroundColor Cyan
if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe --version
} else {
    Write-Host "No .venv yet" -ForegroundColor Yellow
}

Write-Host "Manim in venv:" -ForegroundColor Cyan
if (Test-Path ".venv\Scripts\manim.exe") {
    .\.venv\Scripts\manim.exe --version
} else {
    Write-Host "Not installed yet" -ForegroundColor Yellow
}
