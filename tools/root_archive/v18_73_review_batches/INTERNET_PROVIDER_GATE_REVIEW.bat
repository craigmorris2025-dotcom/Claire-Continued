@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire v17.83 Internet Provider Gate
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.internet.provider_configuration_gate import build_internet_provider_gate; g=build_internet_provider_gate(); print(g['status']); print(g['stop_go']['recommendation']); print('Provider:', g['environment']['selected_provider']); print('Required key present:', g['environment']['required_key_present'])"

echo.
echo Review:
echo data\internet_provider\v17_83_internet_provider_stop_go.md
echo data\internet_provider\provider_config_template.json
echo data\internet_provider\.env.internet.example
echo.
pause
endlocal
