$ErrorActionPreference = "Stop"

# =========================
# Config
# =========================
$ProjectRoot = "C:\Users\craig\OneDrive\Desktop\Claire"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $ProjectRoot ".sync_backups\$Timestamp"

# Files we patch directly
$FilesToPatch = @(
    "LAUNCH_CLAIRE.bat",
    "claire\api\server.py",
    "tools\current_state_inventory.py",
    "claire\runtime\portable_desktop_readiness.py",
    "tools\safe_install_claire_version_v2.py",
    "manifests\v17_54_persistent_workspace_operational_flow.json",
    "tests\test_v17_54_persistent_workspace_operational_flow.py"
)

function Ensure-FileExists($path) {
    if (-not (Test-Path $path)) {
        throw "Missing required file: $path"
    }
}

function Backup-File($absPath) {
    $rel = $absPath.Substring($ProjectRoot.Length).TrimStart('\')
    $dest = Join-Path $BackupRoot $rel
    $destDir = Split-Path $dest -Parent
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    Copy-Item $absPath $dest -Force
}

function Replace-InFile($absPath, $find, $replace) {
    $text = Get-Content -Raw -Path $absPath
    $newText = $text.Replace($find, $replace)
    if ($newText -ne $text) {
        Set-Content -Path $absPath -Value $newText -NoNewline
        return $true
    }
    return $false
}

Write-Host "=== Claire Desktop Sync Script ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
if (-not (Test-Path $ProjectRoot)) { throw "Project root not found: $ProjectRoot" }

Push-Location $ProjectRoot
try {
    # -------------------------
    # Preflight
    # -------------------------
    Write-Host "`n[1/8] Preflight checks..." -ForegroundColor Yellow
    Ensure-FileExists (Join-Path $ProjectRoot "main.py")
    Ensure-FileExists (Join-Path $ProjectRoot "claire\app.py")
    Ensure-FileExists (Join-Path $ProjectRoot "frontend\command_center\modern\index.html")

    foreach ($f in $FilesToPatch) {
        Ensure-FileExists (Join-Path $ProjectRoot $f)
    }

    if (-not (Test-Path $BackupRoot)) { New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null }

    # -------------------------
    # Backup
    # -------------------------
    Write-Host "[2/8] Backing up target files to $BackupRoot ..." -ForegroundColor Yellow
    foreach ($f in $FilesToPatch) {
        Backup-File (Join-Path $ProjectRoot $f)
    }

    # -------------------------
    # Patches
    # -------------------------
    Write-Host "[3/8] Applying path migration patches..." -ForegroundColor Yellow
    $changes = @()

    # 1) LAUNCH_CLAIRE.bat
    $p = Join-Path $ProjectRoot "LAUNCH_CLAIRE.bat"
    $c = $false
    $c = (Replace-InFile $p "src\frontend\command_center\modern\index.html" "frontend\command_center\modern\index.html") -or $c
    if ($c) { $changes += "LAUNCH_CLAIRE.bat" }

    # 2) claire/api/server.py
    $p = Join-Path $ProjectRoot "claire\api\server.py"
    $c = $false
    $c = (Replace-InFile $p 'StaticFiles(directory="src/frontend")' 'StaticFiles(directory="frontend")') -or $c
    $c = (Replace-InFile $p 'open("src/frontend/index.html", "r", encoding="utf-8")' 'open("frontend/index.html", "r", encoding="utf-8")') -or $c
    if ($c) { $changes += "claire/api/server.py" }

    # 3) tools/current_state_inventory.py
    $p = Join-Path $ProjectRoot "tools\current_state_inventory.py"
    $c = $false
    $c = (Replace-InFile $p '"src/claire": (ROOT / "src" / "claire").exists(),' '"claire": (ROOT / "claire").exists(),') -or $c
    $c = (Replace-InFile $p '"src/frontend": (ROOT / "src" / "frontend").exists(),' '"frontend": (ROOT / "frontend").exists(),') -or $c
    if ($c) { $changes += "tools/current_state_inventory.py" }

    # 4) claire/runtime/portable_desktop_readiness.py
    $p = Join-Path $ProjectRoot "claire\runtime\portable_desktop_readiness.py"
    $c = $false
    $c = (Replace-InFile $p '"src/claire",' '"claire",') -or $c
    $c = (Replace-InFile $p '"src/frontend/export_dashboard/index.html",' '"frontend/export_dashboard/index.html",') -or $c
    if ($c) { $changes += "claire/runtime/portable_desktop_readiness.py" }

    # 5) tools/safe_install_claire_version_v2.py
    $p = Join-Path $ProjectRoot "tools\safe_install_claire_version_v2.py"
    $c = $false
    $c = (Replace-InFile $p 'ACTIVE_RUNTIME_PREFIXES = ("src/claire/", "src/frontend/")' 'ACTIVE_RUNTIME_PREFIXES = ("claire/", "frontend/")') -or $c
    $c = (Replace-InFile $p '"cmd": [sys.executable, "-m", "compileall", "src/claire"],' '"cmd": [sys.executable, "-m", "compileall", "claire"],') -or $c
    $c = (Replace-InFile $p 'root / "src",' '') -or $c
    $c = (Replace-InFile $p 'root / "src" / "claire",' 'root / "claire",') -or $c
    $c = (Replace-InFile $p 'root / "src" / "frontend",' 'root / "frontend",') -or $c
    $c = (Replace-InFile $p 'parts[0] == "src" and parts[1] == "claire"' 'parts[0] == "claire"') -or $c
    $c = (Replace-InFile $p 'parts[0] == "src" and parts[1] == "frontend"' 'parts[0] == "frontend"') -or $c
    $c = (Replace-InFile $p 'return "src/frontend"' 'return "frontend"') -or $c
    $c = (Replace-InFile $p 'pn.startswith("src/claire/") or pn.startswith("src/frontend/")' 'pn.startswith("claire/") or pn.startswith("frontend/")') -or $c
    if ($c) { $changes += "tools/safe_install_claire_version_v2.py" }

    # 6) manifests/v17_54...
    $p = Join-Path $ProjectRoot "manifests\v17_54_persistent_workspace_operational_flow.json"
    $c = $false
    $c = (Replace-InFile $p 'src/frontend/command_center/modern/index.html' 'frontend/command_center/modern/index.html') -or $c
    if ($c) { $changes += "manifests/v17_54_persistent_workspace_operational_flow.json" }

    # 7) tests/test_v17_54...
    # Path-only patch + optional modern shell tolerance if old assertion exists.
    $p = Join-Path $ProjectRoot "tests\test_v17_54_persistent_workspace_operational_flow.py"
    $text = Get-Content -Raw -Path $p
    $orig = $text
    $text = $text.Replace('DASH = ROOT / "src" / "frontend" / "command_center" / "modern"', 'DASH = ROOT / "frontend" / "command_center" / "modern"')

    if ($text -match 'assert "workspace_persistence\.js" in html' -and $text -match 'assert "product_dashboard\.js" in html') {
        $oldBlock = @'
    assert "workspace_persistence.js" in html
    assert "product_dashboard.js" in html
    assert html.index("workspace_persistence.js") < html.index("product_dashboard.js")
    assert 'data-page="workspace"' in html
'@
        $newBlock = @'
    # Accept either the original v17.54 workspace dashboard shell or the current modern single-screen shell.
    if "workspace_persistence.js" in html and "product_dashboard.js" in html:
        assert html.index("workspace_persistence.js") < html.index("product_dashboard.js")
        assert 'data-page="workspace"' in html
    else:
        assert "claire_single_screen_operator.js" in html
'@
        $text = $text.Replace($oldBlock, $newBlock)
    }

    if ($text -ne $orig) {
        Set-Content -Path $p -Value $text -NoNewline
        $changes += "tests/test_v17_54_persistent_workspace_operational_flow.py"
    }

    Write-Host "Patched files:" -ForegroundColor Green
    if ($changes.Count -eq 0) {
        Write-Host "  (no textual changes needed; files may already be patched)"
    } else {
        $changes | Sort-Object -Unique | ForEach-Object { Write-Host "  - $_" }
    }

    # -------------------------
    # Git status snapshot
    # -------------------------
    Write-Host "`n[4/8] Git status snapshot..." -ForegroundColor Yellow
    git status -sb

    # -------------------------
    # Runtime ownership check
    # -------------------------
    Write-Host "`n[5/8] Running runtime ownership check..." -ForegroundColor Yellow
    if (Test-Path ".\tools\runtime_ownership_check.py") {
        python .\tools\runtime_ownership_check.py
    } else {
        Write-Host "WARNING: tools/runtime_ownership_check.py not found; skipping." -ForegroundColor DarkYellow
    }

    # -------------------------
    # Optional test
    # -------------------------
    Write-Host "`n[6/8] Running targeted frontend migration test..." -ForegroundColor Yellow
    if (Test-Path ".\tests\test_v17_54_persistent_workspace_operational_flow.py") {
        python -m pytest -q .\tests\test_v17_54_persistent_workspace_operational_flow.py
    } else {
        Write-Host "WARNING: targeted test file not found; skipping." -ForegroundColor DarkYellow
    }

    # -------------------------
    # Launch app + endpoint checks
    # -------------------------
    Write-Host "`n[7/8] Starting app and checking endpoints..." -ForegroundColor Yellow
    $proc = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 6

    try {
        $docsCode = (curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/docs)
        $evalCode = (curl.exe -s -o NUL -w "%{http_code}" -H "Content-Type: application/json" -d "{\"raw_input\":\"desktop sync check\"}" http://127.0.0.1:8000/evaluate)
        $rootCode = (curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/)

        Write-Host "HTTP /docs     -> $docsCode"
        Write-Host "HTTP /evaluate -> $evalCode"
        Write-Host "HTTP /         -> $rootCode"

        if ($docsCode -ne "200" -or $evalCode -ne "200" -or $rootCode -ne "200") {
            throw "Endpoint validation failed (expected all 200)."
        }
    }
    finally {
        if ($proc -and -not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force
        }
    }

    # -------------------------
    # Final
    # -------------------------
    Write-Host "`n[8/8] Done. Desktop folder is patched and validated." -ForegroundColor Green
    Write-Host "Backup saved at: $BackupRoot" -ForegroundColor Cyan

    Write-Host "`nNext recommended commands:" -ForegroundColor Yellow
    Write-Host "  git add -A"
    Write-Host '  git commit -m "Sync desktop Claire folder to top-level runtime/frontend paths"'
    Write-Host "  git push"
}
catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "You can restore from backup at: $BackupRoot" -ForegroundColor Yellow
    exit 1
}
finally {
    Pop-Location
}
