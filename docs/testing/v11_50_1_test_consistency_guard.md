# Claire v11.50.1 Test Consistency Guard

## Problem

Full pytest is repeatedly being destabilized by older placeholder tests and baseline assumptions that no longer match the current Claire maturity state.

Typical failure shape:

- `NotImplementedError: Import target class`
- old stage tests never bound to real runtime classes
- baseline checks expecting zero records/failures while the system now has installed proof/governance infrastructure

## Rule

A test may be one of three things:

1. Active proof test — must import a real class and pass.
2. Bound stage contract test — must point to a real stage/runtime class.
3. Future placeholder — must be underscore-disabled, documented, or marked until the target class exists.

A placeholder test must not break full pytest.

## Validation

```bat
pytest tests/consistency -v
pytest tests/operational_proof -v
python tools/pytest_consistency_audit.py
pytest
```

This installer does not modify runtime, scoring, routing, dashboard, or core_run_output.
