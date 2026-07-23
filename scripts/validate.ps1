$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    npm run check
    docker compose --file compose.yaml config --quiet
}
finally {
    Pop-Location
}
