[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
Push-Location $repoRoot

try {
    $trackedEnv = & git ls-files -- ".env"
    if ($trackedEnv) {
        throw "A runtime .env file is tracked by Git."
    }

    $secretPattern = "sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|[0-9]{8,10}:[A-Za-z0-9_-]{30,}|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY"
    $secretFiles = & git grep -Il -E $secretPattern -- `
        "." ":(exclude)docs/source/**" ":(exclude).env.example"
    if ($LASTEXITCODE -notin @(0, 1)) {
        throw "Tracked-file secret scan failed to run."
    }
    if ($secretFiles) {
        Write-Host "Potential secret material was found in:"
        $secretFiles | ForEach-Object { Write-Host " - $_" }
        throw "Tracked-file secret scan failed."
    }

    & npm audit --omit=dev --audit-level=critical
    if ($LASTEXITCODE -ne 0) {
        throw "A critical production dependency advisory is active."
    }
    & git diff --check
    if ($LASTEXITCODE -ne 0) {
        throw "Git whitespace validation failed."
    }
}
finally {
    Pop-Location
}

Write-Host "Security gate passed: no tracked runtime env, no detected token material, no critical production advisory."
