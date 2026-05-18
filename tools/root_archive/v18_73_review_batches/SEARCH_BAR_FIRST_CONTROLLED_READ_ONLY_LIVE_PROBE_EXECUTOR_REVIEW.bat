@echo off
echo Claire Syntalion v18.31 First Controlled Read-Only Live Probe Executor Review
echo.
echo Expected invariants:
echo - Live probe executor lifecycle can initialize
echo - Transport guard remains active
echo - Outbound network remains blocked
echo - No HTTP request is sent
echo - No response headers or body are fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_31_first_controlled_read_only_live_probe_executor.py -q
echo.
pause
