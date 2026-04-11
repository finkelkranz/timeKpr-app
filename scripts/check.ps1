# Lokale sjekker (Windows PowerShell)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python ikke funnet i PATH. Installer Python 3.11+ eller aktiver virtuelt miljø."
}

python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/mal_prosjekt
python -m pytest -q
Write-Host "OK: ruff, mypy, pytest"
