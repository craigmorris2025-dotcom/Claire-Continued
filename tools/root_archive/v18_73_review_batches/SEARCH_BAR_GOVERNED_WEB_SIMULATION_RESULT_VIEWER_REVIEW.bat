@echo off
echo Claire Syntalion v18.07 - Governed Web Simulation Result Viewer Contract Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_07_governed_web_simulation_result_viewer_contract.py -q
echo.
echo Expected:
echo - simulation result cards are dashboard-safe
echo - bad source flags are forced false
echo - approval remains separate from execution
echo - viewer summary remains non-executing
echo - dashboard rewiring is still not performed
echo.
pause
