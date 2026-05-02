@echo off
setlocal
cd /d "%~dp0"
set CLAIRE_APP_SHELL=1
".venv\Scripts\python.exe" "tools\portable_launcher.py" --live --app
endlocal
