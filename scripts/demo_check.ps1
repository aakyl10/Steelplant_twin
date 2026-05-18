$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

Set-Location $ProjectRoot

function Invoke-DemoStep {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Title,
        [Parameter(Mandatory = $true)]
        [string] $Command,
        [string[]] $Arguments = @()
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Title"
    }
}

Write-Host "Steelplant Twin demo quick check" -ForegroundColor Green
Write-Host "Project root: $ProjectRoot"
Write-Host "Python: $Python"
Write-Host ""
Write-Host "Live MQTT demo commands are intentionally separate:"
Write-Host "  Terminal 1: python -m ingestion.mqtt_to_influx"
Write-Host "  Terminal 2: python -m simulator.publisher"

Invoke-DemoStep "Docker services" "docker" @("compose", "ps")
Invoke-DemoStep "ML SEC regression" $Python @("-m", "ml.train_sec_regression")
Invoke-DemoStep "Pytest" $Python @("-m", "pytest")
Invoke-DemoStep "Ruff" $Python @("-m", "ruff", "check", ".")

Write-Host ""
Write-Host "Demo quick check completed." -ForegroundColor Green
