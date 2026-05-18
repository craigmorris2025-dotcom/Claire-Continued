@echo off
echo ============================================
echo CLAIRE V18.41 ORCHESTRATOR VALIDATION
echo ============================================

python -m pytest tests/test_v18_41_governed_live_search_orchestrator_foundation.py -q

pause
