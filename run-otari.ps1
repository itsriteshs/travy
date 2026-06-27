Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location "$PSScriptRoot\otari"

if (-not (Test-Path '.env')) {
  @'
OTARI_PORT=8010
OTARI_POSTGRES_PORT=5434
'@ | Set-Content -NoNewline .env
}

if (-not (Test-Path 'config.yml')) {
  Copy-Item config.example.yml config.yml
}

docker compose up -d
docker compose ps

Write-Host 'Otari should be reachable at http://127.0.0.1:8010/health' -ForegroundColor Green
