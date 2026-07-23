[CmdletBinding()]
param(
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$composeFile = Join-Path $repoRoot "compose.yaml"
$backupRoot = if ($OutputDirectory) {
    [IO.Path]::GetFullPath($OutputDirectory)
}
else {
    Join-Path $repoRoot "backups"
}

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$backupRoot = (Resolve-Path -LiteralPath $backupRoot).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$staging = Join-Path $backupRoot "staging-$timestamp-$([Guid]::NewGuid().ToString('N'))"
$archivePath = Join-Path $backupRoot "mezie-brandos-$timestamp.zip"
New-Item -ItemType Directory -Path $staging | Out-Null

function Assert-SafeStagingPath {
    $resolvedRoot = [IO.Path]::GetFullPath($backupRoot).TrimEnd(
        [IO.Path]::DirectorySeparatorChar
    )
    $resolvedStage = [IO.Path]::GetFullPath($staging)
    $prefix = "$resolvedRoot$([IO.Path]::DirectorySeparatorChar)"
    if (-not $resolvedStage.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a staging path outside the selected backup directory."
    }
}

Push-Location $repoRoot
try {
    & docker compose --file $composeFile ps --status running postgres api | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "BrandOS postgres and API containers must be running."
    }

    $databaseUser = (
        & docker compose --file $composeFile exec -T postgres printenv POSTGRES_USER
    ).Trim()
    $databaseName = (
        & docker compose --file $composeFile exec -T postgres printenv POSTGRES_DB
    ).Trim()
    if (-not $databaseUser -or -not $databaseName) {
        throw "Could not resolve the configured PostgreSQL identity."
    }

    & docker compose --file $composeFile exec -T postgres pg_dump `
        "--username=$databaseUser" "--dbname=$databaseName" --format=custom `
        --file=/tmp/brandos-backup.dump
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL backup failed." }
    & docker compose --file $composeFile cp `
        postgres:/tmp/brandos-backup.dump (Join-Path $staging "database.dump")
    if ($LASTEXITCODE -ne 0) { throw "Could not copy the PostgreSQL backup." }

    & docker compose --file $composeFile exec -T api tar -czf `
        /tmp/brandos-vault.tar.gz -C /app/vault .
    if ($LASTEXITCODE -ne 0) { throw "Vault backup failed." }
    & docker compose --file $composeFile exec -T api tar -czf `
        /tmp/brandos-storage.tar.gz -C /app/storage .
    if ($LASTEXITCODE -ne 0) { throw "Vault or object-storage backup failed." }
    & docker compose --file $composeFile cp `
        api:/tmp/brandos-vault.tar.gz (Join-Path $staging "vault.tar.gz")
    if ($LASTEXITCODE -ne 0) { throw "Could not copy the vault backup." }
    & docker compose --file $composeFile cp `
        api:/tmp/brandos-storage.tar.gz (Join-Path $staging "storage.tar.gz")
    if ($LASTEXITCODE -ne 0) { throw "Could not copy the storage backup." }

    $migration = (
        & docker compose --file $composeFile exec -T postgres psql `
            "--username=$databaseUser" "--dbname=$databaseName" `
            --tuples-only --no-align --command "SELECT version_num FROM alembic_version;"
    ).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $migration) {
        throw "Could not read the active migration version."
    }

    $files = @("database.dump", "vault.tar.gz", "storage.tar.gz")
    $hashes = @{}
    foreach ($file in $files) {
        $hashes[$file] = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $staging $file)).Hash
    }
    $manifest = [ordered]@{
        format_version = 1
        created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        application = "Mezie BrandOS"
        migration = $migration
        files = $hashes
    }
    $manifest | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 `
        -LiteralPath (Join-Path $staging "manifest.json")

    Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $archivePath -CompressionLevel Optimal
    if (-not (Test-Path -LiteralPath $archivePath)) {
        throw "Backup archive was not created."
    }
}
finally {
    & docker compose --file $composeFile exec -T postgres rm -f `
        /tmp/brandos-backup.dump 2>&1 | Out-Null
    & docker compose --file $composeFile exec -T api rm -f `
        /tmp/brandos-vault.tar.gz /tmp/brandos-storage.tar.gz 2>&1 | Out-Null
    Pop-Location
    Assert-SafeStagingPath
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}

Write-Host "Backup verified: $archivePath"
Write-Output $archivePath
