# Oppretter .venv (hvis den mangler) og installerer prosjektet med dev-avhengigheter.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python ikke funnet i PATH. Installer Python 3.11+ og prøv igjen." -ForegroundColor Yellow
    exit 1
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Oppretter .venv ..."
    python -m venv .venv
}

& $venvPython -m pip install --upgrade pip
& (Join-Path $root ".venv\Scripts\pip.exe") install -e ".[dev]"
Write-Host ""
Write-Host "Ferdig. Aktiver miljø:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
