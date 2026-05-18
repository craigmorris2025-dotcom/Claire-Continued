@echo off
setlocal

echo.
echo ===============================================
echo  Claire v17.79 Manual Proof URLs
echo ===============================================
echo.
echo Make sure START_CLAIRE_SAFE.bat is running first.
echo.

start "" "http://127.0.0.1:8000/docs"
start "" "http://127.0.0.1:8000/operator/dashboard/state"
start "" "http://127.0.0.1:8000/operator/search/capabilities"
start "" "http://127.0.0.1:8000/runtime/truth"
start "" "http://127.0.0.1:8000/routes/audit"
start "" "http://127.0.0.1:8000/autodesign/handoff"
start "" "http://127.0.0.1:8000/design-portal/output"
start "" "http://127.0.0.1:8000/internet/readiness"
start "" "http://127.0.0.1:8000/updates/regression-lock"
start "" "http://127.0.0.1:8000/proof/platform-smoke"
start "" "http://127.0.0.1:8000/desktop/startup"
start "" "http://127.0.0.1:8000/proof/manual-browser-swagger"

echo.
echo Also inspect:
echo data\proof\manual_browser_swagger_proof_binder.md
echo data\proof\manual_browser_swagger_evidence_template.json
echo.
endlocal
