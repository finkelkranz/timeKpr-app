# Oppretter lokalt Git-repo (første gang). Krever at Git er installert.
# Kjør fra prosjektmappen: .\scripts\init-git.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git ble ikke funnet. Installer fra https://git-scm.com/download/win og kjør skriptet igjen." -ForegroundColor Yellow
    exit 1
}

if (Test-Path (Join-Path $root ".git")) {
    Write-Host "Det finnes allerede en .git-mappe her. Ingen endring." -ForegroundColor Green
    exit 0
}

git init
git add .
git commit -m "Første versjon av mal-prosjekt"
Write-Host "Ferdig: lokalt Git-repo opprettet. Neste steg: legg til GitHub-remote, se docs/BEGINNER.md" -ForegroundColor Green
