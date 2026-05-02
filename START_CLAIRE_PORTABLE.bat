@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "tools\portable_launcher.py"
  goto :eof
)
py -3 "tools\portable_launcher.py"
if errorlevel 1 (
  python "tools\portable_launcher.py"
)
