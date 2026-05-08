# Claire Forward Install Rule

Claire is allowed to move forward, but future installers must be manifest-gated.

## Required installer behavior

Every installer must:

1. Declare every file it creates or replaces.
2. Back up every replaced file before writing.
3. Avoid active runtime pollution from demo, placeholder, generated, or proof-only files.
4. Write an install manifest under `.claire_install/reports/`.
5. Preserve `/docs` launch path.
6. Preserve protected runtime imports.
7. Avoid adding placeholder tests to active pytest.
8. Keep incomplete scaffolds disabled until implemented.
9. Never place nested repos under `src/claire`.

## Protected runtime paths

- `main.py`
- `src/claire/app.py`
- `src/claire/api/`
- `src/claire/orchestrator/`
- `src/claire/lifecycle/`
- `src/claire/engines/`
- `src/claire/output/`
- `src/claire/dashboard/`
- `src/claire/technology/technology_intelligence.py`

## Current policy

Forward movement is allowed only through controlled installers.
Blind additive installs are not allowed.
