@echo off
echo Claire Syntalion v18.09 - Governed Web Simulation Dashboard Route Adapter Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_09_governed_web_simulation_dashboard_route_adapter.py -q
echo.
echo Expected:
echo - route adapter exists
echo - route is described but not mounted
echo - dashboard_rewired remains false
echo - no live web execution
echo - no runtime truth mutation
echo - no AI-agent execution
echo - no automatic updates
echo.
pause
