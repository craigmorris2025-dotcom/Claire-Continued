@echo off
echo ============================================
echo CLAIRE V18.47 RETRY TIMEOUT GOVERNANCE
echo ============================================

python -m pytest tests/test_v18_47_controlled_search_retry_timeout_governance.py -q

pause
