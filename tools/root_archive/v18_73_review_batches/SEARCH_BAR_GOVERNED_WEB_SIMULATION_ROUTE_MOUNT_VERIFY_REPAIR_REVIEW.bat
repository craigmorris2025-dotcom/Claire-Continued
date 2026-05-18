@echo off
echo Claire Syntalion v18.11.1 - Route Mount Verifier Repair Review
echo.
echo Running repaired v18.11 gate...
python -m pytest tests/test_v18_11_governed_web_simulation_route_mount_verifier.py -q
echo.
echo Running v18.11.1 repair gate...
python -m pytest tests/test_v18_11_1_governed_web_simulation_route_mount_verifier_repair.py -q
echo.
echo Expected:
echo - explicit supplied app mutation request is NOT honored
echo - production_app_mutated remains false
echo - supplied app receives zero routers
echo - probe app only is used for mountability proof
echo - no live web execution
echo - no runtime truth mutation
echo - no AI-agent execution
echo - no automatic updates
echo.
pause
