@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire v17.81 Cleanup Review Only
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.cleanup.cleanup_proof import build_cleanup_proof; r=build_cleanup_proof(); print(r['status']); print(r['stop_go']['recommendation'])"

echo.
echo Review:
echo data\cleanup\CLEANUP_REVIEW_ONLY.md
echo data\cleanup\archive_plan_do_not_execute.json
echo.
echo Nothing has been deleted or archived.
echo.
pause
endlocal
