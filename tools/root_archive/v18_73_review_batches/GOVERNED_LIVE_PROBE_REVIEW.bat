@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire v17.84 Governed Live Probe Review
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.internet.governed_live_probe import build_probe_contract; c=build_probe_contract(); print(c['status']); print(c['recommendation']); print('Provider:', c['provider']['provider']); print('Key present:', c['provider']['key_present'])"

echo.
echo Review:
echo data\internet_live_probe\v17_84_governed_live_probe_stop_go.md
echo.
echo To run an actual single-query probe, use Swagger:
echo POST /internet/live-probe/run
echo confirm_text: RUN GOVERNED WEB PROBE
echo.
pause
endlocal
