@echo off
echo ============================================
echo CLAIRE V18.45 DASHBOARD RENDERING CONTRACT
echo ============================================

python -m pytest tests/test_v18_45_live_dashboard_result_rendering_contract.py -q

pause
