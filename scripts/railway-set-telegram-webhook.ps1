[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$ApiBaseUrl,

  [string]$EnvPath = ".env",

  [switch]$DryRun,

  [switch]$KeepPendingUpdates
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-DotEnvValue {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Name
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  $escapedName = [regex]::Escape($Name)
  $line = Get-Content -LiteralPath $Path |
    Where-Object { $_ -match "^\s*$escapedName\s*=" } |
    Select-Object -Last 1

  if (-not $line) {
    return $null
  }

  $value = ($line -replace "^\s*$escapedName\s*=\s*", "").Trim()
  if (
    ($value.StartsWith('"') -and $value.EndsWith('"')) -or
    ($value.StartsWith("'") -and $value.EndsWith("'"))
  ) {
    $value = $value.Substring(1, $value.Length - 2)
  }

  return $value
}

function Resolve-SecretValue {
  param([Parameter(Mandatory = $true)][string]$Name)

  $value = [Environment]::GetEnvironmentVariable($Name)
  if ([string]::IsNullOrWhiteSpace($value)) {
    $value = Get-DotEnvValue -Path $EnvPath -Name $Name
  }

  return $value
}

$botToken = Resolve-SecretValue -Name "TELEGRAM_BOT_TOKEN"
$webhookSecret = Resolve-SecretValue -Name "TELEGRAM_WEBHOOK_SECRET"

if ([string]::IsNullOrWhiteSpace($botToken)) {
  throw "TELEGRAM_BOT_TOKEN is missing. Set it in the environment or in $EnvPath."
}

if ([string]::IsNullOrWhiteSpace($webhookSecret)) {
  throw "TELEGRAM_WEBHOOK_SECRET is missing. Set it in the environment or in $EnvPath."
}

$baseUrl = $ApiBaseUrl.TrimEnd("/")
$parsedBaseUrl = [Uri]$baseUrl
if ($parsedBaseUrl.Scheme -ne "https") {
  throw "ApiBaseUrl must be the deployed HTTPS Railway API URL."
}
if ($parsedBaseUrl.Host -in @("localhost", "127.0.0.1")) {
  throw "ApiBaseUrl must not point at a local development server."
}

$webhookUrl = "$baseUrl/api/v1/telegram/webhook"
$telegramSetWebhookUrl = "https://api.telegram.org/bot$botToken/setWebhook"
$body = @{
  url = $webhookUrl
  secret_token = $webhookSecret
  allowed_updates = @("message", "edited_message")
  drop_pending_updates = -not $KeepPendingUpdates.IsPresent
} | ConvertTo-Json -Depth 4

if ($DryRun.IsPresent) {
  Write-Output "Dry run OK. Telegram webhook would be configured for $webhookUrl"
  exit 0
}

$response = Invoke-RestMethod `
  -Method Post `
  -Uri $telegramSetWebhookUrl `
  -ContentType "application/json" `
  -Body $body

if (-not $response.ok) {
  throw "Telegram setWebhook failed: $($response.description)"
}

Write-Output "Telegram webhook configured for $webhookUrl"
