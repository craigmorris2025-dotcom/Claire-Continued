@echo off
setlocal

cd /d "%~dp0"

REM Create venv if missing
if not exist ".venv" (
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate

REM Install dependencies
pip install -q -r requirements.txt

REM Run app (correct module path)
cd src
uvicorn claire.main:app --reload

pause
endlocal