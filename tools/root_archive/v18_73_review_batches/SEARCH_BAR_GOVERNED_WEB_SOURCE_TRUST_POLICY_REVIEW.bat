@echo off
echo Claire Syntalion v18.15 - Governed Web Source Trust Policy Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_15_governed_web_source_trust_policy.py -q
echo.
echo Expected:
echo - source trust policy exists
echo - source tiers are graded
echo - read-only candidates can be identified
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
