@echo off
echo ============================================
echo CLAIRE V18.44 TRUST NORMALIZATION
echo ============================================

python -m pytest tests/test_v18_44_search_trust_scoring_normalization.py -q

pause
