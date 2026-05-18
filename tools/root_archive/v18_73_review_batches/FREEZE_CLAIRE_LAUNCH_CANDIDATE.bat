@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire Syntalion v17.80 Launch Candidate Freeze
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.platform.launch_candidate_freeze import build_launch_candidate_freeze; f=build_launch_candidate_freeze(); print(f['status']); print(f['stop_go']['recommendation'])"

echo.
echo Freeze report:
echo data\launch_candidate\v17_80_launch_candidate_stop_go.md
echo.
pause
endlocal
