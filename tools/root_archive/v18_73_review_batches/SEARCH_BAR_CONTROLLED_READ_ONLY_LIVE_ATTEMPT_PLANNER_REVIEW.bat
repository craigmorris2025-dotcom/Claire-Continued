@echo off
echo Claire Syntalion v18.23 Controlled Read-Only Live Attempt Planner Review
echo.
echo Expected invariants:
echo - Provider preview becomes read-only live attempt plan
echo - Planned URL is not fetched
echo - No HTTP client is invoked
echo - No real network calls
echo - No external requests
echo - No response body fetched
echo - No runtime truth mutation
echo - No automatic updates
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_23_controlled_read_only_live_attempt_planner.py -q
echo.
pause
