# Claire v17.78 Desktop Startup Reliability Checklist

Generated: 2026-05-13T11:19:00.433094Z

## Run

```bat
python -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q
START_CLAIRE_SAFE.bat
VERIFY_CLAIRE_STARTUP.bat
```

## Confirm URLs

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/operator/dashboard/state
- http://127.0.0.1:8000/operator/search/capabilities
- http://127.0.0.1:8000/platform/launch-hardening
- http://127.0.0.1:8000/desktop/startup

## Expected

- Backend imports successfully.
- Swagger opens.
- Dashboard opens.
- Dashboard says Backend Online after refresh.
- Search capabilities endpoint responds.
- Live internet remains disabled.
- Automatic updates remain disabled.

## Stop / Go

Status: **STOP**

Recommendation: Fix desktop startup blockers before packaging or launch-candidate freeze.

### Blockers
- missing_startup_file:safe_launcher
- missing_startup_file:startup_verifier
- package_group_missing:launch:safe_launcher,startup_verifier
- primary_launcher_does_not_start_uvicorn_claire_app
- safe_launcher_does_not_start_uvicorn_claire_app

### Warnings
- prior_launch_hardening_stop_go_is_STOP
- prior_platform_smoke_is_STOP
