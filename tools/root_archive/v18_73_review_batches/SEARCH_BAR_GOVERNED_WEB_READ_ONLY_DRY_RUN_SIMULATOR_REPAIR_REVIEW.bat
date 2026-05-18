@echo off
echo Claire Syntalion v18.17.1 - Governed Read-Only Live Web Dry-Run Simulator Repair Review
echo.
echo Running repaired v18.17 gate...
python -m pytest tests/test_v18_17_governed_web_read_only_dry_run_simulator.py -q
echo.
echo Running v18.17.1 repair gate...
python -m pytest tests/test_v18_17_1_governed_web_read_only_dry_run_simulator_repair.py -q
echo.
pause
