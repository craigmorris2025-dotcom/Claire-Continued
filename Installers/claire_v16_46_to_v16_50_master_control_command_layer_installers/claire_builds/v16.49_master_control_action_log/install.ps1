# Claire Syntalion v16.49_master_control_action_log installer
# Run from the extracted installer folder.
$ErrorActionPreference = "Stop"

$InstallerRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $InstallerRoot
if (!(Test-Path (Join-Path $ProjectRoot "src"))) {
  Write-Host "Project root not detected one level up. Select Claire project root." -ForegroundColor Yellow
  $ProjectRoot = Read-Host "Enter full Claire project root path"
}

$BackupRoot = Join-Path $ProjectRoot "backups\$version"
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null

$Files = @(
  @{ Source = "payload\src/claire/runtime/master_control_action_log.py"; Dest = "src/claire/runtime/master_control_action_log.py" },
  @{ Source = "payload\tests/regression/test_v16_49_master_control_action_log.py"; Dest = "tests/regression/test_v16_49_master_control_action_log.py" }
)

foreach ($File in $Files) {
  $Source = Join-Path $InstallerRoot $File.Source
  $Dest = Join-Path $ProjectRoot $File.Dest
  $DestDir = Split-Path -Parent $Dest
  New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
  if (Test-Path $Dest) {
    $BackupDest = Join-Path $BackupRoot $File.Dest
    $BackupDir = Split-Path -Parent $BackupDest
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    Copy-Item $Dest $BackupDest -Force
  }
  Copy-Item $Source $Dest -Force
  Write-Host "Installed $($File.Dest)" -ForegroundColor Green
}

$InstallManifestDir = Join-Path $ProjectRoot "data\runtime\install_manifests"
New-Item -ItemType Directory -Force -Path $InstallManifestDir | Out-Null
$ManifestPath = Join-Path $InstallManifestDir "v16.49_master_control_action_log.json"
$Manifest = @{
  version = "v16.49_master_control_action_log"
  installed_at = (Get-Date).ToUniversalTime().ToString("o")
  protected_runtime_spine = "preserved"
  rollback_backup = $BackupRoot
  files = $Files | ForEach-Object { $_.Dest }
} | ConvertTo-Json -Depth 6
$Manifest | Set-Content -Path $ManifestPath -Encoding UTF8
Write-Host "Install manifest written: $ManifestPath" -ForegroundColor Cyan
Write-Host "v16.49_master_control_action_log install complete." -ForegroundColor Cyan
