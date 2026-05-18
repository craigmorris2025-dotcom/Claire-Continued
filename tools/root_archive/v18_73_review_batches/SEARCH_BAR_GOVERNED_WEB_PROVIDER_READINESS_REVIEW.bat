@echo off
echo Claire Syntalion v18.12 - Governed Web Provider Readiness Contract Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_12_governed_web_provider_readiness_contract.py -q
echo.
echo Expected:
echo - provider readiness contract exists
echo - complete contract can be marked ready for future read-only dry-run
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
