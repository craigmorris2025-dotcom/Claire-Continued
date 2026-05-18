
@echo off
echo Claire Syntalion v18.19 Controlled Read-Only Live Connectivity Handshake Stub Review
echo.
echo Expected invariants:
echo - No real network calls
echo - No external requests
echo - No runtime truth mutation
echo - No automatic updates
echo - AI-agent execution disabled
echo - Live web execution disabled by default
echo - Approval never equals execution
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_19_controlled_read_only_live_connectivity_handshake_stub.py -q
echo.
pause
