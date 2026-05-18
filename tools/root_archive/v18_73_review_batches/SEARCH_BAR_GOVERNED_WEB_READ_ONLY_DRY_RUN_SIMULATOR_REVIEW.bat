@echo off
echo Claire Syntalion v18.17 - Governed Read-Only Live Web Dry-Run Simulator Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_17_governed_web_read_only_dry_run_simulator.py -q
echo.
echo Expected:
echo - dry-run simulator exists
echo - simulated evidence packets can be produced
echo - no real network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
