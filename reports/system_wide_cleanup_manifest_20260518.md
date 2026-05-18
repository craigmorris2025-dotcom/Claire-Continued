# Claire System-Wide Cleanup Manifest

Date: 2026-05-18

## Goal

Bring the current Claire project into an enterprise-grade, operationally verifiable structure without losing real platform capability.

Desired product shape:

- `backend/` - API/runtime/backend service layer.
- `frontend/` - cockpit, dashboards, command center, operator UI.
- `claire/` - AI/intelligence platform code: lifecycle, governance, portfolio, acquisition, recursive memory, design, live-web governance, route intelligence.
- root support - `main.py`, launchers, requirements, configs, tests, tools, docs, selected data/runtime support.

Canonical product truth:

- governed lifecycle intelligence platform.
- canonical 30-stage lifecycle.
- discovery-first route flow.
- portfolio/acquisition as primary early path.
- breakthrough/design escalation is conditional.
- governed live-web/hybrid mode is blocked by default until explicit gates pass.
- dashboard is an operator cockpit, not static UI.

## Current State Summary

Current live project root is heavily polluted, but active source appears syntactically healthy.

Measured live folder state:

| Path | Files | Size MB | Classification |
| --- | ---: | ---: | --- |
| `claire/` | 3,199 | 16.50 | KEEP_ACTIVE_CORE |
| `frontend/` | 652 | 3.20 | KEEP_ACTIVE_FRONTEND, then consolidate dashboards |
| `tests/` | 729 | 4.94 | KEEP_ACTIVE_TESTS, then prune obsolete duplicate tests only after coverage map |
| `tools/` | 254 | 0.85 | KEEP_ROOT_SUPPORT, then split build/audit/runtime tools |
| `data/` | 814 | 375.81 | KEEP_SELECTED_RUNTIME_DATA, archive large historical run/proof data |
| `runtime/` | 73 | 0.61 | KEEP_RUNTIME_SUPPORT |
| `reports/` | 410 | 29.81 | ARCHIVE_PROOF except active cleanup reports |
| `docs/` | 255 | 102.96 | KEEP_SELECTED_DOCS, archive old build docs |
| `exports/` | 36,119 | 2,142.68 | ARCHIVE_OR_EXTERNALIZE, not product root |
| `archive/` | 854 | 4.83 | ARCHIVE_EXTERNAL |
| `backups/` | 693 | 5.69 | ARCHIVE_EXTERNAL |
| `quarantine_legacy_placeholders/` | 1,868 | 27.86 | ARCHIVE_EXTERNAL or DELETE after snapshot |
| `audits/`, `audit/`, `output/`, `operations/`, `runtime_reports/` | mixed | mixed | ARCHIVE_PROOF unless currently read by runtime |
| `__pycache__/`, `.pytest_cache/`, `*.pyc` | generated | generated | DELETE_GENERATED |

Root file pollution:

- multiple installer scripts at root.
- duplicate launchers and launcher backups.
- `version.json` plus many `version.json.bak_*` files.
- `.env` is present and must remain private / not shipped.
- `README.md` is missing while `pyproject.toml` declares it as readme.
- root `__init__.py` appears unnecessary.

## Verified So Far

Non-destructive syntax checks:

- `claire`, `tools`, and `tests`: 1,918 Python files compiled successfully.
- root installers: 8 of 9 compile.
- broken installer: `install_claire_v19_89_8_s1351_s1450_system_fit_operator_cockpit_v2.py` has an unterminated string literal at line 1516.
- `_FIXED` variant of that installer compiles.

Environment/running status:

- no live root `.venv` exists in current project.
- Windows `py` launcher has no installed Python behind it in this environment.
- bundled Codex Python has `pip`, but did not initially include project runtime dependencies such as `fastapi` and `pytest`.
- full runtime and pytest verification requires rebuilding a local `.venv` or otherwise installing dependencies.

## Major Structural Problems

1. No active root `backend/` folder.
   Git tracks a deleted legacy `backend/`, but active backend behavior is currently inside `claire/api`, `claire/engines`, `claire/runtime`, and adjacent packages. Creating the desired `backend/` tree requires intentional extraction/wrapping.

2. No active root `src/` folder.
   `main.py` and `pytest.ini` still reference `src`, but the folder is absent. This is stale path logic.

3. Dashboard entrypoint mismatch.
   Latest active dashboard work is endpoint-mapped dashboard v3 under `frontend/command_center/modern`; launcher opens `frontend/cockpit/shell/cockpit_shell.html`.

4. Installer sprawl.
   Root contains staged repair installers. These are historical build artifacts, not product source. One is broken.

5. Generated output dominates repository.
   `exports/` alone is about 2.1 GB and 36k files. This should not live in the product repo root.

6. Proof/archive/data mixed with product source.
   Reports, audits, outputs, runtime snapshots, archive trees, quarantine trees, and old generated packages are interleaved with active source.

7. Git state is not diligence-ready.
   Massive deleted/modified/untracked state makes provenance unclear.

8. Packaging metadata stale.
   `README.md` is missing but referenced by `pyproject.toml`; `backend*` is included in package discovery but `backend/` does not exist.

9. Runtime verification blocked until dependencies are restored.
   The code compiles, but FastAPI/TestClient tests cannot run until dependencies are installed.

10. Multiple frontend strata.
   `frontend/command_center/modern`, `frontend/cockpit`, `frontend/export_dashboard`, `frontend/unified`, and older dashboard assets coexist. They need a canonical UI map.

## Initial Classification Rules

### Keep Active

- `claire/`
- `frontend/`
- `tests/`
- `tools/`
- `main.py`
- `requirements.txt`
- `pyproject.toml`
- `pytest.ini`
- `pytest_runtime.ini`
- `LICENSE`
- `.env.example`
- `.gitignore`
- `.gitattributes`
- selected `data/` runtime fixtures and seed state
- selected `runtime/` current state needed by active routes
- selected `docs/` product docs

### Move To Archive/Proof Outside Product Root

- `exports/`
- `archive/`
- `backups/`
- `_claire_archives/`
- `quarantine_legacy_placeholders/`
- most `reports/`
- most `audits/` and `audit/`
- most `output/`
- most `operations/`
- `runtime_reports/`
- root installer scripts after choosing canonical installer history
- root version backups
- launcher backups

### Delete Generated After Snapshot

- `__pycache__/`
- `.pytest_cache/`
- all `*.pyc`
- transient `pytest_full_current.txt`
- generated cache directories

### Needs Review Before Move

- `.claire_install/`
- `install_manifests/`
- `manifests/`
- `claire_build_manifest.json`
- `version.json`
- `data/`
- `runtime/`
- `output/dashboard_endpoint_map/`

## Proposed Enterprise Target Tree

```text
Claire/
  backend/
    api/
    runtime/
    services/
    adapters/
    schemas/
    app.py
  claire/
    lifecycle/
    governance/
    governed_web/
    portfolio/
    acquisition/
    breakthrough/
    design/
    memory/
    recursive/
    research/
    technology/
    validation/
    runtime_truth/
  frontend/
    cockpit/
    command_center/
    shared/
    assets/
  data/
    seed/
    runtime/
    memory/
    proof_minimal/
  docs/
    product/
    architecture/
    operation/
  tests/
  tools/
  config/
  runtime/
  main.py
  LAUNCH_CLAIRE.bat
  requirements.txt
  pyproject.toml
  README.md
```

Important: `backend/` should initially be a thin enterprise service layer that wraps/mounts the active `claire.api` code. A massive move of all API modules out of `claire/` should happen only after runtime tests are green.

## Recommended Execution Order

1. Freeze snapshot outside active product tree.
2. Rebuild local Python environment.
3. Run route/runtime/dashboard smoke tests before cleanup.
4. Create `docs/proof/current_state/` or external proof archive, then move generated proof/export/history out of root.
5. Delete generated caches only after snapshot.
6. Canonicalize launcher to open active dashboard v3 through `main.py`.
7. Add/restore `README.md`.
8. Remove or archive broken root installer, keep `_FIXED` or latest dashboard installer in proof archive only.
9. Add thin `backend/` entry layer after tests are green.
10. Run compile, tests, API smoke, and browser dashboard verification.

## Do Not Do Yet

- Do not delete `data/` wholesale.
- Do not move `claire/api` into `backend/` in one large refactor.
- Do not delete old dashboard shells until launcher/dashboard v3 is verified.
- Do not remove tests just because they are numerous.
- Do not enable live web or body reads during cleanup.

