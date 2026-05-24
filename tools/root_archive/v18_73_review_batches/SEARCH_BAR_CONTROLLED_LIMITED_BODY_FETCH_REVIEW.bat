@echo off
echo ============================================
echo CLAIRE V18.36 LIMITED BODY FETCH VALIDATION
echo ============================================

set PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET=1

python -m pytest tests/test_v18_36_controlled_get_limited_body_fetch.py -q

pause
