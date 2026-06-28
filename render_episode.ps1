# Physics Visual Reels - Episode Pipeline Runner
# Usage: .\render_episode.ps1 <episode-slug>
# Example: .\render_episode.ps1 001-gravity-spacetime

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$EpisodeSlug
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "=== Physics Visual Reels - Pipeline ==="  -ForegroundColor Cyan
Write-Host "Episode: $EpisodeSlug" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $python)) {
    $python = "python"
}

# Step 1: Validate script
$scriptJson = Join-Path $ProjectRoot "episodes\$EpisodeSlug\script.json"
if (!(Test-Path $scriptJson)) {
    Write-Host "[1/4] Script not found. Generate it first:" -ForegroundColor Yellow
    Write-Host "  $python src/generate_script.py --topic 'your topic here'" -ForegroundColor Yellow
    exit 1
}
Write-Host "[1/4] Validating script..." -ForegroundColor Green
& $python (Join-Path $ProjectRoot "src\validate_script.py") --file $scriptJson
if ($LASTEXITCODE -ne 0) {
    Write-Host "Script validation failed. Fix errors and retry." -ForegroundColor Red
    exit 1
}

# Step 2: Generate voiceover
$voiceover = Join-Path $ProjectRoot "episodes\$EpisodeSlug\voiceover.mp3"
if (!(Test-Path $voiceover)) {
    Write-Host "[2/4] Generating voiceover..." -ForegroundColor Green
    & $python (Join-Path $ProjectRoot "src\generate_voiceover.py") --episode $EpisodeSlug
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Voiceover generation failed." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/4] Voiceover already exists, skipping." -ForegroundColor Gray
}

# Step 3: Render Manim scene
$sceneFile = Join-Path $ProjectRoot "episodes\$EpisodeSlug\scene.py"
if (!(Test-Path $sceneFile)) {
    Write-Host "[3/4] Manim scene not found: $sceneFile" -ForegroundColor Yellow
    Write-Host "  Create the scene.py file for this episode, then re-run." -ForegroundColor Yellow
    exit 1
}

$rendersDir = Join-Path $ProjectRoot "outputs\renders"
if (!(Test-Path $rendersDir)) {
    New-Item -ItemType Directory -Path $rendersDir | Out-Null
}

Write-Host "[3/4] Rendering Manim scene..." -ForegroundColor Green
$manimExe = Join-Path $ProjectRoot ".venv\Scripts\manim.exe"
if (!(Test-Path $manimExe)) {
    $manimExe = "manim"
}
& $manimExe render -qh --format mp4 $sceneFile
if ($LASTEXITCODE -ne 0) {
    Write-Host "Manim render failed." -ForegroundColor Red
    exit 1
}

# Find the rendered file and copy to outputs
$rendered = Get-ChildItem -Path (Join-Path $ProjectRoot "media") -Filter "*.mp4" -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($rendered) {
    $silentOutput = Join-Path $rendersDir "$EpisodeSlug-silent.mp4"
    Copy-Item $rendered.FullName $silentOutput -Force
    Write-Host "  Silent render saved: $silentOutput" -ForegroundColor Green
} else {
    Write-Host "  Rendered MP4 not found in media folder." -ForegroundColor Yellow
    exit 1
}

# Step 4: Assemble final video
Write-Host "[4/4] Assembling final video..." -ForegroundColor Green
& $python (Join-Path $ProjectRoot "src\assemble_final.py") --episode $EpisodeSlug
if ($LASTEXITCODE -ne 0) {
    Write-Host "Assembly failed." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Pipeline complete! ===" -ForegroundColor Cyan
Write-Host "Final video: outputs\final\$EpisodeSlug-final.mp4" -ForegroundColor Green
