@echo off
echo Claire Syntalion v18.28 Read-Only Transport Selection Gate Review
echo.
echo Expected invariants:
echo - Null transport remains default
echo - Real transport may only be selected as review-only candidate
echo - Real transport is not allowed to execute
echo - No HTTP client is invoked
echo - Planned URL is not fetched
echo - No real network calls
echo - No response body fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_28_read_only_transport_selection_gate.py -q
echo.
pause
