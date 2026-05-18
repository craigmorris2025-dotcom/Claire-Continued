@echo off
echo Claire Syntalion v18.26 Pre-Live Probe Authorization Audit Review
echo.
echo Expected invariants:
echo - Probe execution gate becomes pre-live authorization audit
echo - Authorization can become ready for next build
echo - authorization_granted remains false
echo - execution_gate_passed remains false
echo - execution_permitted remains false
echo - No HTTP client is invoked
echo - Planned URL is not fetched
echo - No real network calls
echo - No external requests
echo - No response body fetched
echo - No runtime truth mutation
echo.
python -m pytest tests/test_v18_26_pre_live_probe_authorization_audit.py -q
echo.
pause
