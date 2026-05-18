@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire v17.85 Evidence Promotion Review
echo ===============================================
echo.

set PYTHON_EXE=python
if exist ".venv\Scripts\python.exe" set PYTHON_EXE=.venv\Scripts\python.exe

%PYTHON_EXE% -c "from claire.internet.evidence_promotion_gate import build_evidence_promotion_gate; g=build_evidence_promotion_gate(); print(g['status']); print(g['stop_go']['recommendation']); print('Candidates:', g['candidate_count']); print('Quarantine:', g['quarantine_count'])"

echo.
echo Review:
echo data\internet_evidence\v17_85_evidence_promotion_stop_go.md
echo data\internet_evidence\promoted_evidence_candidates_template.json
echo data\internet_evidence\quarantine_review_queue.json
echo.
pause
endlocal
