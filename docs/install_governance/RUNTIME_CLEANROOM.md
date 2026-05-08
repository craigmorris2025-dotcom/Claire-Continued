# Claire Runtime Cleanroom

v16.27 establishes a clean runtime testing surface.

## What this means

The full repository can still contain generated exports, docs, historical proof packs, and archived scaffolds.

The active runtime surface must remain:

- importable
- syntax clean
- launchable
- testable without generated placeholder tests

## Placeholder test policy

Generated tests that only contain `raise NotImplementedError("Import target class")` are not valid active tests.

They belong in:

`tests/placeholder_disabled/`

They can be restored later only after they are connected to real target classes.

## Runtime test command

Use:

`pytest -c pytest_runtime.ini`

instead of full `pytest tests` during stabilization.

## Runtime compile command

Use:

`python tools/runtime_compile_check.py`
