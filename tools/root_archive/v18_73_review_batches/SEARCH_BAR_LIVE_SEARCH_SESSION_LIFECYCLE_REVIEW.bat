@echo off
echo ============================================
echo CLAIRE V18.42 SESSION LIFECYCLE VALIDATION
echo ============================================

python -m pytest tests/test_v18_42_real_live_search_session_lifecycle.py -q

pause
