[CmdletBinding()]
param(
  [string]$ExportDir,

  [switch]$UseRailwayApiDatabase,

  [switch]$UseRailwaySshTunnel,

  [switch]$UseTemporaryRailwayTcpProxy,

  [int]$TunnelPort = 15432,

  [switch]$Prod,

  [ValidateSet("replace", "append")]
  [string]$Mode = "replace"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-TcpPort {
  param(
    [Parameter(Mandatory = $true)][string]$HostName,
    [Parameter(Mandatory = $true)][int]$Port
  )

  $client = New-Object System.Net.Sockets.TcpClient
  try {
    $connect = $client.BeginConnect($HostName, $Port, $null, $null)
    if (-not $connect.AsyncWaitHandle.WaitOne(1000)) {
      return $false
    }
    $client.EndConnect($connect)
    return $true
  } catch {
    return $false
  } finally {
    $client.Close()
  }
}

function Get-RailwayVariableMap {
  param([Parameter(Mandatory = $true)][string]$Service)

  $raw = & railway variable list --service $Service --json
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to read Railway variable names for service $Service."
  }
  $parsed = $raw | ConvertFrom-Json
  $map = @{}
  if ($parsed.PSObject.Properties.Name -contains "variables") {
    foreach ($property in $parsed.variables.PSObject.Properties) {
      $map[$property.Name] = [string]$property.Value
    }
  } else {
    foreach ($property in $parsed.PSObject.Properties) {
      $map[$property.Name] = [string]$property.Value
    }
  }
  return $map
}

function New-PostgresUrl {
  param(
    [Parameter(Mandatory = $true)][hashtable]$Vars,
    [Parameter(Mandatory = $true)][string]$HostName,
    [Parameter(Mandatory = $true)][int]$Port
  )

  foreach ($key in @("PGUSER", "PGPASSWORD", "PGDATABASE")) {
    if ([string]::IsNullOrWhiteSpace($Vars[$key])) {
      throw "Postgres variable $key is missing."
    }
  }

  $user = [Uri]::EscapeDataString($Vars["PGUSER"])
  $password = [Uri]::EscapeDataString($Vars["PGPASSWORD"])
  $database = [Uri]::EscapeDataString($Vars["PGDATABASE"])
  return "postgresql+psycopg://${user}:${password}@${HostName}:${Port}/${database}"
}

function Start-RailwayTunnel {
  param(
    [Parameter(Mandatory = $true)][int]$Port,
    [Parameter(Mandatory = $true)][string]$StdOutPath,
    [Parameter(Mandatory = $true)][string]$StdErrPath
  )

  $railwayCommand = Get-Command railway -ErrorAction Stop
  $railwayArgs = @(
    "connect",
    "Postgres",
    "--environment",
    "production",
    "--tunnel-only",
    "--port",
    "$Port"
  )

  if ($railwayCommand.Source -like "*.ps1") {
    $hostProcess = (Get-Process -Id $PID).Path
    $powershellArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $railwayCommand.Source) + $railwayArgs
    return Start-Process `
      -FilePath $hostProcess `
      -ArgumentList $powershellArgs `
      -WindowStyle Hidden `
      -RedirectStandardOutput $StdOutPath `
      -RedirectStandardError $StdErrPath `
      -PassThru
  }

  return Start-Process `
    -FilePath $railwayCommand.Source `
    -ArgumentList $railwayArgs `
    -WindowStyle Hidden `
    -RedirectStandardOutput $StdOutPath `
    -RedirectStandardError $StdErrPath `
    -PassThru
}

$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot
$previousDatabaseUrl = [Environment]::GetEnvironmentVariable("DATABASE_URL", "Process")
$tunnelProcess = $null
$createdTcpProxyId = $null
try {
  $railwayModeCount = @($UseRailwayApiDatabase, $UseRailwaySshTunnel, $UseTemporaryRailwayTcpProxy) |
    Where-Object { $_.IsPresent } |
    Measure-Object |
    Select-Object -ExpandProperty Count
  if ($railwayModeCount -gt 1) {
    throw "Choose only one Railway database export mode."
  }

  if ([string]::IsNullOrWhiteSpace($ExportDir)) {
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $ExportDir = Join-Path $repoRoot "data/convex-export/$timestamp"
  }

  $resolvedExportDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ExportDir)
  New-Item -ItemType Directory -Force -Path $resolvedExportDir | Out-Null

  $exportCommand = @(
    "uv",
    "run",
    "--directory",
    "apps/api",
    "python",
    "../../scripts/export-convex-jsonl.py",
    "--output",
    $resolvedExportDir
  )

  if ($UseRailwayApiDatabase.IsPresent) {
    $railwayArgs = @("run", "--service", "api", "--environment", "production", "--no-local", "--")
    & railway @railwayArgs @exportCommand
  } elseif ($UseRailwaySshTunnel.IsPresent) {
    $tunnelOut = Join-Path $resolvedExportDir "railway-tunnel.out.log"
    $tunnelErr = Join-Path $resolvedExportDir "railway-tunnel.err.log"
    $tunnelProcess = Start-RailwayTunnel `
      -Port $TunnelPort `
      -StdOutPath $tunnelOut `
      -StdErrPath $tunnelErr

    $ready = $false
    foreach ($attempt in 1..30) {
      if (Test-TcpPort -HostName "127.0.0.1" -Port $TunnelPort) {
        $ready = $true
        break
      }
      Start-Sleep -Seconds 1
    }
    if (-not $ready) {
      throw "Railway SSH tunnel did not open on 127.0.0.1:$TunnelPort."
    }

    $postgresVars = Get-RailwayVariableMap -Service "Postgres"
    $env:DATABASE_URL = New-PostgresUrl -Vars $postgresVars -HostName "127.0.0.1" -Port $TunnelPort
    & $exportCommand[0] @($exportCommand[1..($exportCommand.Length - 1)])
  } elseif ($UseTemporaryRailwayTcpProxy.IsPresent) {
    $proxyList = & railway tcp-proxy list --service Postgres --json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) {
      throw "Failed to list Railway TCP proxies."
    }

    $proxy = @($proxyList.proxies) | Select-Object -First 1
    if (-not $proxy) {
      $created = & railway tcp-proxy create --port 5432 --service Postgres --json | ConvertFrom-Json
      if ($LASTEXITCODE -ne 0) {
        throw "Failed to create temporary Railway TCP proxy."
      }
      $proxy = $created.proxy
      $createdTcpProxyId = $proxy.id
    }

    foreach ($attempt in 1..30) {
      if ($proxy.syncStatus -eq "ACTIVE") {
        break
      }
      Start-Sleep -Seconds 1
      $status = & railway tcp-proxy status $proxy.id --service Postgres --json | ConvertFrom-Json
      if ($LASTEXITCODE -ne 0) {
        throw "Failed to read Railway TCP proxy status."
      }
      $proxy = $status.proxy
    }
    if ($proxy.syncStatus -ne "ACTIVE") {
      throw "Temporary Railway TCP proxy did not become active."
    }

    $postgresVars = Get-RailwayVariableMap -Service "Postgres"
    $env:DATABASE_URL = New-PostgresUrl -Vars $postgresVars -HostName $proxy.domain -Port ([int]$proxy.proxyPort)
    & $exportCommand[0] @($exportCommand[1..($exportCommand.Length - 1)])
  } else {
    & $exportCommand[0] @($exportCommand[1..($exportCommand.Length - 1)])
  }
  if ($LASTEXITCODE -ne 0) {
    throw "SQL export failed with exit code $LASTEXITCODE."
  }

  $manifestPath = Join-Path $resolvedExportDir "manifest.json"
  if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Expected manifest was not written: $manifestPath"
  }
  $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

  foreach ($table in $manifest.tables) {
    $importArgs = @("convex", "import", "--table", $table.table, $table.path, "--format", "jsonLines")
    if ($Mode -eq "replace") {
      $importArgs += @("--replace", "--yes")
    } else {
      $importArgs += "--append"
    }
    if ($Prod.IsPresent) {
      $importArgs += "--prod"
    }

    & npx @importArgs
    if ($LASTEXITCODE -ne 0) {
      throw "Convex import failed for table $($table.table) with exit code $LASTEXITCODE."
    }
  }

  Write-Output "Imported $($manifest.row_count) SQL rows across $($manifest.table_count) Convex tables."
  Write-Output "Manifest: $manifestPath"
} finally {
  if ($null -ne $previousDatabaseUrl) {
    $env:DATABASE_URL = $previousDatabaseUrl
  } else {
    Remove-Item Env:\DATABASE_URL -ErrorAction SilentlyContinue
  }
  if ($null -ne $tunnelProcess -and -not $tunnelProcess.HasExited) {
    Stop-Process -Id $tunnelProcess.Id -Force -ErrorAction SilentlyContinue
  }
  if ($null -ne $createdTcpProxyId) {
    & railway tcp-proxy delete $createdTcpProxyId --service Postgres --yes --json *> $null
  }
  Pop-Location
}
