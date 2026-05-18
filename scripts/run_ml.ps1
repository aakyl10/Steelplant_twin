$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython } else { "python" }

Set-Location $ProjectRoot

Write-Host "Running ML SEC regression evidence pipeline" -ForegroundColor Cyan
Write-Host "Python: $Python"
& $Python -m ml.train_sec_regression

if ($LASTEXITCODE -ne 0) {
    throw "ML pipeline failed."
}
