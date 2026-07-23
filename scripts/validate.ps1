$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    npm run check
    docker compose --file compose.yaml config --quiet
    & (Join-Path $PSScriptRoot "security-check.ps1")
}
finally {
    Pop-Location
}
