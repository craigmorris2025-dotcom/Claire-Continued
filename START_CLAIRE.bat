@echo off
setlocal
cd /d "%~dp0"
".venv\Scripts\python.exe" "tools\portable_launcher.py" --live
endlocal
