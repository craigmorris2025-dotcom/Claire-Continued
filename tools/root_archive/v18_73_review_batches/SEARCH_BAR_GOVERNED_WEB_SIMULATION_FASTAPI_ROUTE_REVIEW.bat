@echo off
echo Claire Syntalion v18.10 - Governed Web Simulation FastAPI Route Registration Shim Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_10_governed_web_simulation_fastapi_route_registration.py -q
echo.
echo Expected:
echo - FastAPI route shim exists
echo - route registration is explicit only
echo - dashboard_rewired remains false
echo - no live web execution
echo - no runtime truth mutation
echo - no AI-agent execution
echo - no automatic updates
echo.
pause
