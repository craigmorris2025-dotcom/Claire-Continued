@echo off
echo ============================================
echo CLAIRE V18.46 PROVIDER ADAPTER VALIDATION
echo ============================================

set CLAIRE_ALLOW_REAL_SEARCH_PROVIDER=1

python -m pytest tests/test_v18_46_real_controlled_internet_search_provider_adapter.py -q

pause
