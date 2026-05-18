@echo off
echo Claire Syntalion v18.14 - Governed Web Rate Limit Policy Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_14_governed_web_rate_limit_policy.py -q
echo.
echo Expected:
echo - rate-limit policy contract exists
echo - request ceilings and cooldowns are defined
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
