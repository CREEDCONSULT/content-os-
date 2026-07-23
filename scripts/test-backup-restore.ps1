[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$composeFile = Join-Path $repoRoot "compose.yaml"
$backupRoot = Join-Path $repoRoot "backups"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
$backupRoot = (Resolve-Path -LiteralPath $backupRoot).Path
$staging = Join-Path $backupRoot "recovery-test-$([Guid]::NewGuid().ToString('N'))"
$testDatabase = "brandos_restore_test_$([Guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $staging | Out-Null

function Assert-SafeStagingPath {
    $resolvedRoot = [IO.Path]::GetFullPath($backupRoot).TrimEnd(
        [IO.Path]::DirectorySeparatorChar
    )
    $resolvedStage = [IO.Path]::GetFullPath($staging)
    $prefix = "$resolvedRoot$([IO.Path]::DirectorySeparatorChar)"
    if (-not $resolvedStage.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a recovery-test path outside the repository backup directory."
    }
}

Push-Location $repoRoot
try {
    $backupPath = (& (Join-Path $PSScriptRoot "backup.ps1") | Select-Object -Last 1)
    Expand-Archive -LiteralPath $backupPath -DestinationPath $staging
    $manifest = Get-Content -Raw -LiteralPath (Join-Path $staging "manifest.json") |
        ConvertFrom-Json
    foreach ($file in @("database.dump", "vault.tar.gz", "storage.tar.gz")) {
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $staging $file)).Hash
        if ($actual -ne $manifest.files.$file) { throw "Checksum mismatch: $file" }
    }

    $databaseUser = (
        & docker compose --file $composeFile exec -T postgres printenv POSTGRES_USER
    ).Trim()
    & docker compose --file $composeFile exec -T postgres createdb `
        "--username=$databaseUser" $testDatabase
    if ($LASTEXITCODE -ne 0) { throw "Could not create isolated recovery-test database." }
    & docker compose --file $composeFile cp `
        (Join-Path $staging "database.dump") postgres:/tmp/brandos-recovery-test.dump
    if ($LASTEXITCODE -ne 0) { throw "Could not stage the recovery-test dump." }
    & docker compose --file $composeFile exec -T postgres pg_restore `
        --no-owner "--username=$databaseUser" "--dbname=$testDatabase" `
        /tmp/brandos-recovery-test.dump
    if ($LASTEXITCODE -ne 0) { throw "Isolated database restore failed." }
    $brandCount = (
        & docker compose --file $composeFile exec -T postgres psql `
            "--username=$databaseUser" "--dbname=$testDatabase" `
            --tuples-only --no-align --command "SELECT count(*) FROM brands;"
    ).Trim()
    if ($LASTEXITCODE -ne 0 -or [int]$brandCount -lt 1) {
        throw "Restored database did not contain the expected brand record."
    }
    Write-Host "Recovery proof passed: migration $($manifest.migration), brand records $brandCount"
}
finally {
    if ($databaseUser) {
        & docker compose --file $composeFile exec -T postgres dropdb `
            --if-exists --force "--username=$databaseUser" `
            $testDatabase 2>&1 | Out-Null
    }
    & docker compose --file $composeFile exec -T postgres rm -f `
        /tmp/brandos-recovery-test.dump 2>&1 | Out-Null
    Pop-Location
    Assert-SafeStagingPath
    if (Test-Path -LiteralPath $staging) {
        Remove-Item -LiteralPath $staging -Recurse -Force
    }
}
