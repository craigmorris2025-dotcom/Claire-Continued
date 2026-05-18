@echo off
echo ============================================
echo CLAIRE V18.37 SEARCH PARSER CONTRACT
echo ============================================

python -m pytest tests/test_v18_37_search_result_parser_contract.py -q

pause
