$ErrorActionPreference = "Stop"

$WslProjectDir = "/mnt/c/Users/freezemyself/Desktop/praktika/todo_app"

Write-Host "Running BASIC-2 endpoint check..."
Write-Host ""

wsl.exe -d Ubuntu -- bash -lc "cd '$WslProjectDir' && uv sync && bash scripts/run_curl_check.sh"
