@echo off
echo ============================================
echo CLAIRE V18.40 GOVERNANCE HARDENING VALIDATION
echo ============================================

python -m pytest tests/test_v18_40_governance_error_state_hardening.py -q

pause
