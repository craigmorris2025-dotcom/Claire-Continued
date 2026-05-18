# Claire v19 Backend Import + App Bootproof Audit

- Generated: `2026-05-10T20:20:06.493120Z`
- Stop/Go: **GO_BACKEND_BOOTPROOF_BASELINE**
- Syntax failures excluding quarantine/backups: **0**
- claire.app import ok: **True**
- create_app exists: **True**
- create_app ok: **True**
- App type: `FastAPI`

## Route Summary
- Route count: **28**
- Unique path count: **25**
- Has root `/`: **True**
- Has `/health`: **True**
- Has `/docs`: **True**
- Has dashboard routes: **True**
- Has runtime routes: **False**
- Has search routes: **True**
- Has web/internet routes: **False**

### Route Path Sample
- `/`
- `/api/dashboard/search/live`
- `/api/dashboard/search/provider/probe`
- `/api/dashboard/search/provider/status`
- `/api/dashboard/search/smoke/google`
- `/dashboard/alignment/buttons`
- `/dashboard/alignment/capabilities`
- `/dashboard/alignment/status`
- `/dashboard/alignment/verify`
- `/dashboard/payload`
- `/dashboard/payload/status`
- `/docs`
- `/docs/oauth2-redirect`
- `/evaluate`
- `/health`
- `/openapi.json`
- `/operator/dashboard/state`
- `/operator/search`
- `/operator/search/capabilities`
- `/operator/search/live`
- `/operator/search/query`
- `/operator/search/run`
- `/operator/search/smoke/google`
- `/pipeline/evaluate`
- `/redoc`

## Errors
- None.

## Remaining Syntax Failures
- None detected outside excluded quarantine/backups.

## Next Step
- Proceed to canonical dashboard payload bridge audit/build.
