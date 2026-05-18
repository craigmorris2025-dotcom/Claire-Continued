@echo off
echo Claire Syntalion v18.16 - Governed Web Read-Only Dry-Run Eligibility Gate Review
echo.
echo Running pytest gate...
python -m pytest tests/test_v18_16_governed_web_read_only_dry_run_gate.py -q
echo.
echo Expected:
echo - eligibility gate combines provider, allowlist, rate-limit, and source trust policy
echo - complete request can be eligible for future read-only dry-run
echo - no network call is performed
echo - live web remains disabled
echo - execution remains disabled
echo - runtime truth mutation remains disabled
echo - AI-agent execution remains disabled
echo - automatic updates remain disabled
echo.
pause
