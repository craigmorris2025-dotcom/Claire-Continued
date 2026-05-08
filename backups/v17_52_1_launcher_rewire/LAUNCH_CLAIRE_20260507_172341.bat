@echo off
setlocal EnableExtensions

REM ============================================================
REM Claire Root Launcher
REM Version: 11.42
REM Active Dashboard: src\frontend\command_center\modern\index.html
REM Purpose:
REM   One clean project-root launcher.
REM   Opens modern command center only.
REM   Does not call old dashboard shell.
REM ============================================================

cd /d "%~dp0"

set "CLAIRE_ROOT=%~dp0"
set "CLAIRE_APP_SHELL=0"
set "CLAIRE_LAUNCH_MODE=modern_dashboard_root"
set "CLAIRE_DASHBOARD_PATH=src\frontend\command_center\modern\index.html"
set "CLAIRE_LOG_DIR=logs"

if not exist "%CLAIRE_LOG_DIR%" mkdir "%CLAIRE_LOG_DIR%"

echo.
echo ============================================================
echo Claire Syntalion - Root Launcher v11.42
echo Root: %CLAIRE_ROOT%
echo Dashboard: %CLAIRE_DASHBOARD_PATH%
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "CLAIRE_PYTHON=.venv\Scripts\python.exe"
) else (
    set "CLAIRE_PYTHON=python"
)

echo Using Python: %CLAIRE_PYTHON%
echo.

if exist "tools\desktop_version_sync.py" (
    echo Syncing desktop/version state...
    "%CLAIRE_PYTHON%" "tools\desktop_version_sync.py" --root "%CLAIRE_ROOT%" --mode consolidated_root > "%CLAIRE_LOG_DIR%\desktop_version_sync.out.log" 2> "%CLAIRE_LOG_DIR%\desktop_version_sync.err.log"
)

if exist "%CLAIRE_DASHBOARD_PATH%" (
    echo Opening modern Claire dashboard...
    start "" "%CLAIRE_DASHBOARD_PATH%"
    goto :done
)

echo.
echo [Claire Launcher Error]
echo Modern dashboard not found:
echo   %CLAIRE_DASHBOARD_PATH%
echo.
echo Install the modern dashboard package first, or verify this folder exists:
echo   src\frontend\command_center\modern
echo.
pause

:done
echo.
echo Claire modern dashboard launch complete.
endlocal
