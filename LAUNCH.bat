
@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate

pip install -q -r src\backend\requirements.txt

cd src
python main.py

pause
endlocal