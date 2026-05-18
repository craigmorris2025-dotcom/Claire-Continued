@echo off
echo Claire Syntalion v18.22 Governed Web Provider Adapter Preview Bridge Review
echo.
echo Expected invariants:
echo - Governed search envelope becomes provider adapter preview
echo - Preview URL may be constructed but never fetched
echo - No HTTP client is invoked
echo - No real network calls
echo - No external requests
echo - No runtime truth mutation
echo - No automatic updates
echo - execution_performed remains false
echo - network_call_performed remains false
echo - response_body_fetched remains false
echo.
python -m pytest tests/test_v18_22_governed_web_provider_adapter_preview_bridge.py -q
echo.
pause
