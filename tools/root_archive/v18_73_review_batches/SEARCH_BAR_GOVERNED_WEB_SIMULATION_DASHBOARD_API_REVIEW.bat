@echo off
echo Claire Syntalion v18.08 - Governed Web Simulation Dashboard API Contract Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_08_governed_web_simulation_dashboard_api_contract.py -q
echo.
echo Expected:
echo - dashboard API response shape is stable
echo - dashboard_rewired remains false
echo - bad execution flags are forced false
echo - live web remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
