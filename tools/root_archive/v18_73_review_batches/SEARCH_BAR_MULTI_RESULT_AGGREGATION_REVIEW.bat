@echo off
echo ============================================
echo CLAIRE V18.43 MULTI RESULT AGGREGATION
echo ============================================

python -m pytest tests/test_v18_43_governed_multi_result_aggregation.py -q

pause
