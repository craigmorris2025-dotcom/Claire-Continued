# Platform Deployment Guide

## Canonical Runtime

The active runtime package is `runtime_core`. The `backend` package remains only as the ASGI adapter boundary, and the legacy `claire` package is intentionally tombstoned for one release cycle.

Primary entrypoints:

- Local app: `main.py`
- ASGI adapter: `backend.app:app`
- Runtime factory: `runtime_core.app:create_app`
- Windows launcher: `LAUNCH_PLATFORM.bat`
- Dashboard: `http://127.0.0.1:8000/dashboard`

## Local Start

```bat
LAUNCH_PLATFORM.bat
```

Manual start:

```bat
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The platform uses `PLATFORM_*` configuration keys. Keep legacy environment keys out of active code and deployment configuration; the CI migration boundary check enforces that rule.

## Staging Smoke

After deployment, verify these release invariants:

- Mounted route count: `353`
- Dashboard HTML, CSS, and JS return HTTP 200
- Activation registry reports `14` ready pipelines
- `/api/dashboard/state` returns a valid backend-owned payload
- `claire` imports fail with the tombstone message and do not forward to runtime code

## Rollback

Rollback target: the migration-complete tag for the release.

1. Redeploy the tagged build.
2. Restore the database/config snapshot if runtime state changed after the tag.
3. Re-run the staging smoke checks above.
4. If an external integration unexpectedly depends on `claire`, replace the tombstone with a temporary forwarding shim only as an emergency compatibility measure, then open a follow-up migration issue.

## Verification

```bat
.venv\Scripts\python.exe -B -m pytest tests -q --tb=short
.venv\Scripts\python.exe tools\check_migration_boundaries.py
.venv\Scripts\python.exe -m pip check
```
