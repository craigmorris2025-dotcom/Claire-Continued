@echo off
echo Claire Syntalion v18.27.1 Read-Only Probe Executor Null Transport Repair Review
echo.
echo Expected invariants:
echo - Probe executor lifecycle can simulate successfully
echo - Null transport is active
echo - Real transport remains disabled
echo - No sockets created
echo - No HTTP requests performed
echo - No response body fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_27_1_read_only_probe_executor_null_transport_repair.py -q
echo.
pause
