@echo off
echo Claire Syntalion v18.29 Real HTTP Transport Dry Activation Shell Review
echo.
echo Expected invariants:
echo - Real HTTP transport contract can be created
echo - Dry activation mode remains true
echo - Real transport is not allowed to execute
echo - HTTP client is not constructed
echo - Socket creation is forbidden
echo - No request is sent
echo - No response body is fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_29_real_http_transport_dry_activation_shell.py -q
echo.
pause
