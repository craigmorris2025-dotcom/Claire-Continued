@echo off
echo Claire Syntalion v18.18 - Governed Read-Only Live Web Adapter Boundary Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_18_governed_web_read_only_live_adapter_boundary.py -q
echo.
echo Expected:
echo - live web adapter boundary exists
echo - enable request is not honored yet
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
