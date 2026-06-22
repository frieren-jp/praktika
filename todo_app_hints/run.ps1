$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
if ($ProjectDir -notmatch "^([A-Za-z]):\\(.*)$") {
    throw "Cannot convert Windows path to WSL path: $ProjectDir"
}
$Drive = $Matches[1].ToLower()
$Rest = $Matches[2] -replace "\\", "/"
$WslProjectDir = "/mnt/$Drive/$Rest"

Write-Host "Starting BASIC-2 ToDo API..."
Write-Host "Project: $ProjectDir"
Write-Host "URL:     http://127.0.0.1:8000/docs"
Write-Host ""

wsl.exe -d Ubuntu -- bash -lc "cd '$WslProjectDir' && uv sync && uv run uvicorn entrypoints.run:app --host 127.0.0.1 --port 8000"
