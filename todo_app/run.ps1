$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WslProjectDir = "/mnt/c/Users/freezemyself/Desktop/praktika/todo_app"

Write-Host "Starting BASIC-2 ToDo API..."
Write-Host "Project: $ProjectDir"
Write-Host "URL:     http://127.0.0.1:8000/docs"
Write-Host ""

wsl.exe -d Ubuntu -- bash -lc "cd '$WslProjectDir' && uv sync && uv run uvicorn entrypoints.run:app --host 127.0.0.1 --port 8000"
