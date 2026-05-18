@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire v17.82 Archive Approval Gate
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.cleanup.archive_approval_gate import build_archive_approval_gate; g=build_archive_approval_gate(); print(g['status']); print(g['recommendation'])"

echo.
echo Review:
echo data\cleanup\ARCHIVE_APPROVAL_REVIEW.md
echo data\cleanup\approved_archive_moves_template.json
echo.
echo Nothing has been moved or deleted.
echo.
pause
endlocal
