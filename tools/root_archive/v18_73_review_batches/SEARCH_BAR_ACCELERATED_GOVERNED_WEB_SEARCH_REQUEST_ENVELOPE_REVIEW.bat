@echo off
echo Claire Syntalion v18.21 Accelerated Governed Web Search Request Envelope Review
echo.
echo Expected invariants:
echo - Search bar query becomes governed web preview envelope
echo - Dashboard preview payload exists
echo - No real network calls
echo - No external requests
echo - No runtime truth mutation
echo - No automatic updates
echo - execution_performed remains false
echo - network_call_performed remains false
echo - AI-agent execution remains disabled
echo - Live enablement flag still does not execute in this build
echo.
python -m pytest tests/test_v18_21_accelerated_governed_web_search_request_envelope.py -q
echo.
pause
