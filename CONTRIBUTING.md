# Contributing

## Runtime Boundary

Use `runtime_core` for active runtime imports. The legacy `claire` namespace is retired and must remain a tombstone for the deprecation window.

Do not add new legacy environment keys or active `claire` imports. Use `PLATFORM_*` configuration and `runtime_core` imports instead. CI runs `tools/check_migration_boundaries.py` to enforce this.

## Local Verification

Before handing off changes, run:

```bat
.venv\Scripts\python.exe tools\check_migration_boundaries.py
.venv\Scripts\python.exe -B -m pytest tests -q --tb=short
```

For dependency work, also run:

```bat
.venv\Scripts\python.exe -m pip check
.venv\Scripts\pip-audit.exe -l --cache-dir .cache\pip-audit --progress-spinner off
```
