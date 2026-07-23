$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $repoRoot ".env"
$exampleFile = Join-Path $repoRoot ".env.example"

if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath $exampleFile -Destination $envFile
    Write-Host "Created .env from the local-development template."
}

docker compose --file (Join-Path $repoRoot "compose.yaml") up --build --detach
docker compose --file (Join-Path $repoRoot "compose.yaml") ps

Write-Host "Mezie BrandOS is starting at http://localhost:3100"
Write-Host "Local bootstrap username: mezie"
Write-Host "Change the bootstrap password and session secret before remote exposure."
