@echo off
echo ============================================
echo CLAIRE V18.35 METADATA-ONLY PROBE VALIDATION
echo ============================================

set PLATFORM_ALLOW_CONTROLLED_METADATA_GET=1

python -m pytest tests/test_v18_35_controlled_get_metadata_only_probe.py -q

pause
