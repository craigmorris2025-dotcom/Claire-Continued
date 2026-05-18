@echo off
echo ============================================
echo CLAIRE V18.39 LIVE WEB UI WIRING VALIDATION
echo ============================================

python -m pytest tests/test_v18_39_search_bar_live_web_ui_wiring.py -q

pause
