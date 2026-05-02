@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "tools\portable_launcher.py" --live --run-baseline
  goto :eof
)
py -3 "tools\portable_launcher.py" --live --run-baseline
if errorlevel 1 (
  python "tools\portable_launcher.py" --live --run-baseline
)
