param(
	[int]$Port = 8000,
	[switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
	Where-Object { $_.State -eq 'Listen' } |
	Select-Object -First 1

if ($existing) {
	$proc = Get-Process -Id $existing.OwningProcess -ErrorAction SilentlyContinue
	if (-not $Force) {
		$name = if ($proc) { $proc.ProcessName } else { 'unknown' }
		Write-Host "Port $Port is already in use by PID $($existing.OwningProcess) ($name)." -ForegroundColor Yellow
		Write-Host "If this is your backend, keep using it at http://127.0.0.1:$Port" -ForegroundColor Yellow
		Write-Host "Otherwise run: .\\run-backend.ps1 -Port 8001" -ForegroundColor Yellow
		Write-Host "Or force takeover: .\\run-backend.ps1 -Force" -ForegroundColor Yellow
		exit 0
	}

	if ($proc) {
		Stop-Process -Id $existing.OwningProcess -Force
	}
}

Set-Location "$PSScriptRoot\backend"
& .\.venv\Scripts\python.exe -m uvicorn main:app --reload --port $Port
