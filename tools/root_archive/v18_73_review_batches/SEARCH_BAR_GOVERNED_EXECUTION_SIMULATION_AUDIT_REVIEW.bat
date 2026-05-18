@echo off
echo Claire Syntalion v18.06 - Governed Web Execution Simulation Audit Trail Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_06_governed_web_execution_simulation_audit_trail.py -q
echo.
echo Expected:
echo - approval alone does not execute anything
echo - exact confirmation allows simulation eligibility review only
echo - execution_performed remains false
echo - live web execution remains false
echo - runtime truth mutation remains false
echo - AI-agent execution remains false
echo - automatic updates remain false
echo.
pause
