Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Set-Location $PSScriptRoot

if (-not (Test-Path 'backend/.venv/Scripts/python.exe')) {
  py -3.12 -m venv backend/.venv
}

& .\backend\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\backend\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

Set-Location .\frontend
npm install

Write-Host 'All dependencies installed successfully.' -ForegroundColor Green
