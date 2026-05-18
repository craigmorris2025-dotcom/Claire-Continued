@echo off
echo Claire Syntalion v18.13 - Governed Web Allowlist Registry Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_13_governed_web_allowlist_registry.py -q
echo.
echo Expected:
echo - allowlist registry exists
echo - allowlist entries are policy-only
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
