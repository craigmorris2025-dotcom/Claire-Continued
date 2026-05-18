@echo off
echo Claire Syntalion v18.32 First Real Controlled HEAD Handshake Review
echo.
echo Expected invariants:
echo - HEAD handshake layer exists
echo - Response body fetching remains forbidden
echo - Runtime truth mutation remains forbidden
echo - Automatic updates remain forbidden
echo - execution_performed remains false during validation
echo - network_call_performed remains false during validation
echo.
python -m pytest tests/test_v18_32_first_real_controlled_head_handshake.py -q
echo.
pause
