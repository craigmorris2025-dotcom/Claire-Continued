$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$TickScript = Join-Path $Root "tools\continuous_scheduler_tick.py"

Set-Location $Root
& $Python -B $TickScript
exit $LASTEXITCODE
