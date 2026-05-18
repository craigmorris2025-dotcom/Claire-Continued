@echo off
setlocal

echo Claire Syntalion v18.05 - Governed Web Execution Simulation Layer Review
echo.
echo Running v18.05 simulation-only regression test...
python -m pytest tests/test_v18_05_governed_web_execution_simulation_layer.py -q
if errorlevel 1 (
    echo.
    echo v18.05 review FAILED.
    exit /b 1
)

echo.
echo v18.05 review PASSED.
echo Confirmed: simulation only; execution_performed remains false.
endlocal
