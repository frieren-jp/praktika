$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
if ($ProjectDir -notmatch "^([A-Za-z]):\\(.*)$") {
    throw "Cannot convert Windows path to WSL path: $ProjectDir"
}
$Drive = $Matches[1].ToLower()
$Rest = $Matches[2] -replace "\\", "/"
$WslProjectDir = "/mnt/$Drive/$Rest"

Write-Host "Running BASIC-2 endpoint check..."
Write-Host ""

wsl.exe -d Ubuntu -- bash -lc "cd '$WslProjectDir' && uv sync && bash scripts/run_curl_check.sh"
