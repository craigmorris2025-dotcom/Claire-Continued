@echo off
echo Claire Syntalion v18.20 Controlled Live Connectivity Handshake Review Record
echo.
echo Expected invariants:
echo - Review record can be created
echo - Approval does not become execution
echo - No real network calls
echo - No external requests
echo - No runtime truth mutation
echo - No automatic updates
echo - execution_performed remains false
echo - network_call_performed remains false
echo - invalid execution claims are rejected
echo.
python -m pytest tests/test_v18_20_controlled_live_connectivity_handshake_review_record.py -q
echo.
pause
