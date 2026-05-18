@echo off
echo ============================================
echo CLAIRE V18.34.1 IMPORT PATH REPAIR VALIDATION
echo ============================================

set CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=1

python -m pytest tests/test_v18_34_real_head_probe_review_result_capture.py -q

pause
