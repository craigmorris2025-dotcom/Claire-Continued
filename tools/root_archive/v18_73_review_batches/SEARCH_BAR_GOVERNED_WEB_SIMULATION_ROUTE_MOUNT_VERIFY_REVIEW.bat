@echo off
echo Claire Syntalion v18.11 - Governed Web Simulation Route Mount Verifier Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_11_governed_web_simulation_route_mount_verifier.py -q
echo.
echo Expected:
echo - route mount verifier exists
echo - default verification uses probe app only
echo - supplied app is not mutated unless explicitly requested
echo - dashboard_rewired remains false
echo - no live web execution
echo - no runtime truth mutation
echo - no AI-agent execution
echo - no automatic updates
echo.
pause
