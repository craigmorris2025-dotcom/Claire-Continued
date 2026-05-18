# Claire Cleanup Execution Manifest

Date: 2026-05-18

## Cleanup Policy

No source-bearing folder should be deleted during the first cleanup pass.

First pass action:

- move obvious historical/output pollution outside the product root.
- preserve it in a timestamped external archive.
- leave active source, tests, tools, config, data, runtime, and dashboard support in place.
- delete generated caches only after a restorable archive exists.

## Verified Active Roots To Keep In Product

- `claire/`
- `frontend/`
- `tests/`
- `tools/`
- `data/`
- `runtime/`
- `config/`
- `docs/`
- `reports/` for active evaluation reports only
- `main.py`
- `LAUNCH_CLAIRE.bat`
- `requirements.txt`
- `pyproject.toml`
- `pytest.ini`
- `.env.example`
- `.gitignore`
- `.gitattributes`
- `LICENSE`
- `version.json`

## First-Pass External Archive Candidates

Target archive:

`C:\Users\craig\OneDrive\Desktop\Claire_Cleanup_Archive_20260518`

Move these top-level folders out of the product root:

| Path | Files | Size MB | Reason |
| --- | ---: | ---: | --- |
| `exports/` | 36,119 | 2,142.68 | generated export history; too large for product root |
| `archive/` | 854 | 4.83 | historical archive |
| `backups/` | 693 | 5.69 | backup history |
| `_claire_archives/` | 14 | 0.15 | historical archive |
| `quarantine_legacy_placeholders/` | 1,899 | 27.89 | legacy placeholder quarantine |

Move these root files into archive:

- `LAUNCH_CLAIRE_RESTORED_WORKING.bat.bak_A7_20260513_180916`
- `version.json.bak_*`

Delete after archive/snapshot:

- root `__pycache__/`
- root `.pytest_cache/`

## Not Moving In First Pass

These are polluted but may still be referenced by runtime/dashboard/tests and need a narrower second pass:

- `output/`
- `audits/`
- `audit/`
- `runtime_reports/`
- `operations/`
- `install_manifests/`
- `manifests/`
- `.claire_install/`
- most `reports/`
- nested `*.pyc`
- nested `*.bak*`

## Verification Gates

Before cleanup:

- dashboard/action/live/readiness tests pass.
- `/dashboard/payload` has one canonical GET owner.
- `/api/system/file-readiness` reports current pollution.
- `/api/system/route-integrity` reports route state.

After cleanup:

- `/dashboard` still returns HTML.
- `/dashboard/payload` still returns full backend-owned payload.
- `/api/system/file-readiness` still reports active roots present.
- `/api/system/route-integrity` still reports canonical payload owner locked.
- focused tests pass.

## Approval Boundary

This manifest requires explicit execution approval because it moves large folders and deletes generated caches.
