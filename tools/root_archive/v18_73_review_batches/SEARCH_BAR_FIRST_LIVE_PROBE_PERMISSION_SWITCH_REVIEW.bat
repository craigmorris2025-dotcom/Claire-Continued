@echo off
echo Claire Syntalion v18.30 First Live Probe Permission Switch Review
echo.
echo Expected invariants:
echo - Permission switch is installed
echo - Permission can be ready for next build
echo - permission_granted_this_build remains false
echo - Real transport is not allowed to execute
echo - HTTP client is not constructed
echo - Socket creation remains forbidden
echo - No request is sent
echo - No response body is fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_30_first_live_probe_permission_switch.py -q
echo.
pause
