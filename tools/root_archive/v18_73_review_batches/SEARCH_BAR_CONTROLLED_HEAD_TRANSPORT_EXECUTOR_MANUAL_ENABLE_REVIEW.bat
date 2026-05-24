@echo off
echo Claire Syntalion v18.33 Controlled HEAD Transport Executor Manual Enable Review
echo.
echo Safe validation:
echo - No network call unless PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE=1
echo - Response body fetching remains forbidden
echo - Runtime truth mutation remains forbidden
echo - Automatic updates remain forbidden
echo.
python -m pytest tests/test_v18_33_controlled_head_transport_executor_manual_enable.py -q
echo.
echo Optional real HEAD probe:
echo set PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE=1
echo python -c "from claire.governance.governed_web.controlled_head_transport_executor import execute_controlled_head_transport; print(execute_controlled_head_transport({'query':'manual live HEAD probe'}).to_dict())"
echo.
pause
