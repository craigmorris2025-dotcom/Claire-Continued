@echo off
echo Claire Syntalion v18.25 Controlled Probe Execution Gate Review
echo.
echo Expected invariants:
echo - Network probe shell becomes controlled execution gate
echo - Gate is always locked in v18.25
echo - execution_gate_passed remains false
echo - execution_permitted remains false
echo - Probe executor remains disabled
echo - No HTTP client is invoked
echo - Planned URL is not fetched
echo - No real network calls
echo - No external requests
echo - No response body fetched
echo - No runtime truth mutation
echo.
python -m pytest tests/test_v18_25_controlled_probe_execution_gate.py -q
echo.
pause
