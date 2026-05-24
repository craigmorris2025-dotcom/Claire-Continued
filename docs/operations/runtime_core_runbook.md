# Runtime Core Runbook

## Current State

`runtime_core` is the canonical backend runtime. `backend` is the ASGI adapter boundary. `claire/__init__.py` is a deliberate tombstone and should stay in place for at least one release cycle after migration completion.

Deprecation notice: `claire` tombstone present; removal planned after 2 releases or 30 days, whichever is later.

## Release Checks

- Full tests: `.venv\Scripts\python.exe -B -m pytest tests -q --tb=short`
- Migration boundary: `.venv\Scripts\python.exe tools\check_migration_boundaries.py`
- Dependency integrity: `.venv\Scripts\python.exe -m pip check`
- SCA: `.venv\Scripts\pip-audit.exe -l --cache-dir .cache\pip-audit --progress-spinner off`
- Secrets scan: search active files for key-shaped tokens before tagging
- Staging smoke: route count `353`, dashboard assets HTTP 200, activation registry `14/14`

## Emergency Rollback

1. Redeploy the migration-complete tag.
2. Restore the latest database/config backup if state moved after the release.
3. Re-run the staging smoke.
4. Capture the failing route, failing test, and exact commit before applying any hotfix.

## Compatibility Policy

Keep compatibility aliases for routes where tests prove they are still needed. Do not reintroduce legacy runtime imports or legacy config in active code. If an integration misses the deprecation window, use a temporary forwarding shim only for rollback recovery and remove it again after the incident.
