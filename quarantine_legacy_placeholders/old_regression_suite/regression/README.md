# Claire Lifecycle Regression Test Suite

This package adds a lightweight regression harness for the completed Claire v5.28 deterministic lifecycle.

## Files included

```text
tests/regression/test_lifecycle_regression.py
tests/regression/run_lifecycle_smoke.py
tests/regression/fixtures/lifecycle_inputs.py
tests/regression/__init__.py
tests/regression/fixtures/__init__.py
```

## What the suite verifies

The tests assert that:

```text
21 / 21 lifecycle stages are implemented
21 / 21 lifecycle stages are active
partial_stage_count == 0
pending_stage_count == 0
Stage 1 output_key == knowledge_ingestion
Stage 2 output_key == signal_extraction
portfolio_binder.status == success
Knowledge Ingestion and Signal Extraction binder sections exist
core engine outputs exist at the top level
core scores exist in scores
defense/autonomy keeps control-gated posture
climate insurance routes correctly even with mixed signals
```

## Run with pytest

From the project root:

```powershell
$env:PYTHONPATH = ".\src"
python -m pytest tests/regression/test_lifecycle_regression.py -q
```

On macOS/Linux:

```bash
PYTHONPATH=./src python -m pytest tests/regression/test_lifecycle_regression.py -q
```

## Run without pytest

```powershell
$env:PYTHONPATH = ".\src"
python tests/regression/run_lifecycle_smoke.py
```

## Recommended commit

After extracting and passing tests:

```powershell
git add .
git commit -m "v5.29 add lifecycle regression test suite"
```
