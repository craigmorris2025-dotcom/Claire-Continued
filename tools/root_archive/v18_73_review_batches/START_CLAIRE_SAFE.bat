@echo off
REM v18.72 governed web activation flags
set CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=1
set CLAIRE_ALLOW_CONTROLLED_METADATA_GET=1
set CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET=1
set CLAIRE_ALLOW_REAL_SEARCH_PROVIDER=1
REM v18.72 governed web activation flags end

setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire Syntalion v17.78 Safe Desktop Startup
echo ===============================================
echo.
echo Backend:  http://127.0.0.1:8000
echo Swagger:  http://127.0.0.1:8000/docs
echo Dashboard: frontend\command_center\modern\index.html
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

echo Verifying Claire app import...
%PYTHON_EXE% -c "import claire.app; print('Claire app import: OK')" || (
    echo.
    echo Claire app import failed.
    echo Run:
    echo python -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q
    pause
    exit /b 1
)

echo Building desktop startup reliability report...
%PYTHON_EXE% -c "from claire.desktop.startup_reliability import build_desktop_startup_reliability; build_desktop_startup_reliability(); print('Startup reliability report: OK')" || (
    echo.
    echo Startup reliability report failed.
    pause
    exit /b 1
)

echo.
echo Starting Claire backend...
start "Claire Backend v17.78" cmd /k "%PYTHON_EXE% -m uvicorn claire.app:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 7 /nobreak > nul

echo Opening Swagger and dashboard...
start "" "http://127.0.0.1:8000/docs"
start "" "%cd%\frontend\command_center\modern\index.html"

echo.
echo Verify:
echo http://127.0.0.1:8000/operator/dashboard/state
echo http://127.0.0.1:8000/operator/search/capabilities
echo http://127.0.0.1:8000/desktop/startup
echo.
endlocal
