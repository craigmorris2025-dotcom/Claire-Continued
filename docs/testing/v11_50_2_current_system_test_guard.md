# Claire v11.50.2 Current-System Test Guard

Claire has outgrown several older generated placeholder tests. Those tests
contain `NotImplementedError("Import target class")`, so they are not real
runtime validation. Keeping them active makes full pytest inconsistent.

## Current rule

- Real tests stay active.
- Operational proof tests stay active.
- Placeholder stage tests are preserved but quarantined by renaming them with a leading underscore.
- A placeholder can return later only after it is bound to a real current-system class.

## Commands

```bat
python tools\pytest_current_system_guard.py --audit
python tools\pytest_current_system_guard.py --quarantine
pytest tests\consistency -v
pytest tests\operational_proof -v
pytest
```

This package does not modify runtime, routing, scoring, launcher, dashboard, or core_run_output.
