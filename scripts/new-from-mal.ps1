# Kaller Python-skriptet som bytter ut mal-navn. Krever Python 3.11+.
# Eksempel:
#   .\scripts\new-from-mal.ps1 -PipName "mitt-prosjekt" -PackageName "mitt_prosjekt" -CliName "mitt-app"
param(
    [Parameter(Mandatory = $true)][string]$PipName,
    [Parameter(Mandatory = $true)][string]$PackageName,
    [Parameter(Mandatory = $true)][string]$CliName
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Error "Python ikke funnet i PATH."
    exit 1
}

python "$PSScriptRoot\new_from_mal.py" --pip-name $PipName --package-name $PackageName --cli-name $CliName
