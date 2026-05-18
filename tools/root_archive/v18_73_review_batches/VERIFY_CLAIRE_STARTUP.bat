@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire Syntalion v17.78 Startup Verification
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

echo Running targeted test...
%PYTHON_EXE% -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q

echo.
echo Rebuilding startup reliability report...
%PYTHON_EXE% -c "from claire.desktop.startup_reliability import build_desktop_startup_reliability; report = build_desktop_startup_reliability(); print(report['stop_go']['status']); print(report['stop_go']['recommendation'])"

echo.
echo Check report:
echo data\desktop_packaging\startup_reliability_checklist.md
echo.
pause
endlocal
