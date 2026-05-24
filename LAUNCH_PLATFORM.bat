@echo off
setlocal
title Governed Intelligence Platform - Operational Dashboard Launcher

set "PLATFORM_ROOT=%~dp0"
set "PLATFORM_HOST=127.0.0.1"
set "PLATFORM_PORT=8000"

cd /d "%PLATFORM_ROOT%"

echo.
echo ============================================================
echo  Governed Intelligence Platform - Operational Command Center Launcher
echo ============================================================
echo.
echo Backend owns truth. Cockpit presentation only.
echo Runtime authority remains blocked.
echo Opening the permanent local cockpit as the platform dashboard.
echo.

if exist "%PLATFORM_ROOT%.venv\Scripts\python.exe" (
    set "PLATFORM_PYTHON=%PLATFORM_ROOT%.venv\Scripts\python.exe"
) else (
    set "PLATFORM_PYTHON=python"
)

for /f %%p in ('"%PLATFORM_PYTHON%" -B tools\find_open_port.py %PLATFORM_HOST% %PLATFORM_PORT%') do set "PLATFORM_PORT=%%p"
set "PLATFORM_URL=http://%PLATFORM_HOST%:%PLATFORM_PORT%/dashboard"

echo Using Python:
echo   %PLATFORM_PYTHON%
echo Using port:
echo   %PLATFORM_PORT%
echo Dashboard URL:
echo   %PLATFORM_URL%
echo.

start "Platform Backend" /D "%PLATFORM_ROOT%" cmd /k ""%PLATFORM_PYTHON%" -B -m uvicorn main:app --host %PLATFORM_HOST% --port %PLATFORM_PORT%"

echo Waiting for backend health...
for /L %%i in (1,1,20) do (
    "%PLATFORM_PYTHON%" -B -c "import json, urllib.request; print(json.load(urllib.request.urlopen('http://%PLATFORM_HOST%:%PLATFORM_PORT%/health', timeout=2)).get('status'))" >nul 2>nul
    if not errorlevel 1 goto platform_ready
    timeout /t 1 /nobreak >nul
)

echo.
echo Backend did not answer health check yet.
echo Leave the Platform Backend window open and inspect its output.
echo.
pause
goto platform_done

:platform_ready
echo Backend is healthy.
echo Opening %PLATFORM_URL%
start "" "%PLATFORM_URL%"

:platform_done

endlocal
