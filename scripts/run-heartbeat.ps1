$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

docker compose exec -T api .venv/bin/python -m app.heartbeat_runner
