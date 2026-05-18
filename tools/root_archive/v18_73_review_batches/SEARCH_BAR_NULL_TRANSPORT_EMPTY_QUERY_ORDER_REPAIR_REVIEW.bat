@echo off
echo Claire Syntalion v18.27.2 Null Transport Empty Query Order Repair Review
echo.
echo Expected invariants:
echo - Empty query returns invalid_request
echo - Invalid query is checked before authorization readiness
echo - Null transport is active
echo - Real transport remains disabled
echo - No HTTP requests performed
echo - No response body fetched
echo - execution_performed remains false
echo - network_call_performed remains false
echo.
python -m pytest tests/test_v18_27_2_null_transport_empty_query_order_repair.py -q
echo.
pause
