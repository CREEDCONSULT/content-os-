[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [switch]$ConfirmRestore
)

$ErrorActionPreference = "Stop"
if (-not $ConfirmRestore) {
    throw "Restore is destructive. Re-run with -ConfirmRestore after confirming the backup path."
}

$repoRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$composeFile = Join-Path $repoRoot "compose.yaml"
$resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
$backupRoot = Join-Path $repoRoot "backups"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$backupRoot = (Resolve-Path -LiteralPath $backupRoot).Path
$staging = Join-Path $backupRoot "restore-$([Guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $staging | Out-Null
$servicesStopped = $false
$restoreCompleted = $false

function Assert-SafeStagingPath {
    $resolvedRoot = [IO.Path]::GetFullPath($backupRoot).TrimEnd(
        [IO.Path]::DirectorySeparatorChar
    )
    $resolvedStage = [IO.Path]::GetFullPath($staging)
    $prefix = "$resolvedRoot$([IO.Path]::DirectorySeparatorChar)"
    if (-not $resolvedStage.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a restore path outside the repository backup directory."
    }
}

Push-Location $repoRoot
try {
    Expand-Archive -LiteralPath $resolvedBackup -DestinationPath $staging
    $manifestPath = Join-Path $staging "manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Backup manifest is missing."
    }
    $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    if ($manifest.format_version -ne 1) {
        throw "Unsupported backup format."
    }
    foreach ($file in @("database.dump", "vault.tar.gz", "storage.tar.gz")) {
        $path = Join-Path $staging $file
        if (-not (Test-Path -LiteralPath $path)) { throw "Backup file is missing: $file" }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash
        if ($actual -ne $manifest.files.$file) { throw "Checksum mismatch: $file" }
    }

    $preRestoreBackup = (& (Join-Path $PSScriptRoot "backup.ps1") | Select-Object -Last 1)
    Write-Host "Pre-restore safety backup: $preRestoreBackup"

    $databaseUser = (
        & docker compose --file $composeFile exec -T postgres printenv POSTGRES_USER
    ).Trim()
    $databaseName = (
        & docker compose --file $composeFile exec -T postgres printenv POSTGRES_DB
    ).Trim()
    & docker compose --file $composeFile stop api heartbeat web
    if ($LASTEXITCODE -ne 0) { throw "Could not stop BrandOS application services." }
    $servicesStopped = $true
    & docker compose --file $composeFile cp `
        (Join-Path $staging "database.dump") postgres:/tmp/brandos-restore.dump
    if ($LASTEXITCODE -ne 0) { throw "Could not stage the database restore." }
    & docker compose --file $composeFile exec -T postgres pg_restore `
        --clean --if-exists --no-owner "--username=$databaseUser" `
        "--dbname=$databaseName" /tmp/brandos-restore.dump
    if ($LASTEXITCODE -ne 0) { throw "Database restore failed." }

    & docker compose --file $composeFile run --rm --no-deps `
        --volume "${staging}:/restore:ro" api `
        .venv/bin/python -m app.restore_files /app/vault /restore/vault.tar.gz
    if ($LASTEXITCODE -ne 0) { throw "Vault restore failed." }
    & docker compose --file $composeFile run --rm --no-deps `
        --volume "${staging}:/restore:ro" api `
        .venv/bin/python -m app.restore_files /app/storage /restore/storage.tar.gz
    if ($LASTEXITCODE -ne 0) { throw "Object-storage restore failed." }

    & docker compose --file $composeFile up --detach api heartbeat web
    if ($LASTEXITCODE -ne 0) { throw "Could not restart BrandOS." }
    & docker compose --file $composeFile exec -T postgres rm -f /tmp/brandos-restore.dump

    $deadline = (Get-Date).AddMinutes(2)
    do {
        Start-Sleep -Seconds 3
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8000/ready" -TimeoutSec 5
        }
        catch {
            $health = $null
        }
    } until (($health.ok -eq $true) -or (Get-Date) -gt $deadline)
    if ($health.ok -ne $true) { throw "BrandOS did not become ready after restore." }
    $restoreCompleted = $true
}
finally {
    if ($servicesStopped -and -not $restoreCompleted) {
        & docker compose --file $composeFile up --detach api heartbeat web
    }
    Pop-Location
    Assert-SafeStagingPath
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}

Write-Host "Restore verified. BrandOS is ready at http://localhost:3100"
