@echo off
echo Claire Syntalion v18.24 Controlled Network Probe Adapter Shell Review
echo.
echo Expected invariants:
echo - Live attempt plan becomes controlled network probe adapter shell
echo - Probe executor exists as shell only
echo - Probe executor remains hard-disabled
echo - No HTTP client is invoked
echo - Planned URL is not fetched
echo - No real network calls
echo - No external requests
echo - No response body fetched
echo - No runtime truth mutation
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_24_controlled_network_probe_adapter_shell.py -q
echo.
pause
