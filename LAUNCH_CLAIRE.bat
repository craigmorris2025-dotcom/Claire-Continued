@echo off
setlocal
title Claire Syntalion - Operational Dashboard Launcher

set "CLAIRE_ROOT=%~dp0"
set "CLAIRE_HOST=127.0.0.1"
set "CLAIRE_PORT=8000"
set "CLAIRE_URL=http://%CLAIRE_HOST%:%CLAIRE_PORT%/dashboard"

cd /d "%CLAIRE_ROOT%"

echo.
echo ============================================================
echo  Claire Syntalion - Operational Command Center Launcher
echo ============================================================
echo.
echo Backend owns truth. Cockpit presentation only.
echo Runtime authority remains blocked.
echo Opening backend-owned operational cockpit dashboard.
echo.

if exist "%CLAIRE_ROOT%.venv\Scripts\python.exe" (
    set "CLAIRE_PYTHON=%CLAIRE_ROOT%.venv\Scripts\python.exe"
) else (
    set "CLAIRE_PYTHON=python"
)

echo Using Python:
echo   %CLAIRE_PYTHON%
echo.

start "Claire Backend" /D "%CLAIRE_ROOT%" cmd /k ""%CLAIRE_PYTHON%" -B -m uvicorn main:app --host %CLAIRE_HOST% --port %CLAIRE_PORT%"

echo Waiting for backend health...
for /L %%i in (1,1,20) do (
    "%CLAIRE_PYTHON%" -B -c "import json, urllib.request; print(json.load(urllib.request.urlopen('http://%CLAIRE_HOST%:%CLAIRE_PORT%/health', timeout=2)).get('status'))" >nul 2>nul
    if not errorlevel 1 goto claire_ready
    timeout /t 1 /nobreak >nul
)

echo.
echo Backend did not answer health check yet.
echo Leave the Claire Backend window open and inspect its output.
echo.
pause
goto claire_done

:claire_ready
echo Backend is healthy.
echo Opening %CLAIRE_URL%
start "" "%CLAIRE_URL%"

:claire_done

endlocal
