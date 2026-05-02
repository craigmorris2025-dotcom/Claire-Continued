# Baseline Validation

Date: 2026-05-02

Checks run before core lifecycle edits:

- Python syntax check for selected core files: passed after elevated virtualenv execution.
- `node --check src/frontend/export_dashboard/dashboard.js`: passed.
- `node --check src/frontend/js/app.js`: passed.
- `python -B tools/run_claire_baseline.py`: passed, 25 of 25 checks.
- `python -B -m pytest tests -q`: initially failed during collection on legacy `backend.*` imports; after adding a compatibility facade, passed 52 tests.

Pytest collection failures:

- `tests/test_contract.py`: `ModuleNotFoundError: No module named 'backend.claire'`
- `tests/test_engines.py`: `ModuleNotFoundError: No module named 'backend.engines'`
- `tests/test_pipeline.py`: `ModuleNotFoundError: No module named 'backend.claire'`
- `tests/test_scoring.py`: `ModuleNotFoundError: No module named 'backend.scoring'`

Resolution:

The project baseline runner is green. The full pytest suite now passes after adding a thin `backend.*` compatibility facade that preserves legacy imports without moving the active `src/claire` implementation.
