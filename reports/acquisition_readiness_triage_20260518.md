# Claire Syntalion Acquisition-Readiness Triage

Date: 2026-05-18

## Executive Read

Claire is not a simple dashboard project anymore. The current canonical definition and pipeline docs describe a governed lifecycle intelligence platform: signal governance, trend discovery, portfolio intelligence, conditional breakthrough escalation, acquisition packaging, lifecycle memory, and governed live-web activation.

The system appears strategically advanced, but the repository is not yet diligence-ready. The current blocker is presentation and reproducibility, not lack of conceptual depth. An acquirer needs to see a clean operational core, a controlled demo path, a clear governance boundary, and evidence that live connectivity is deliberate rather than accidental.

## Canonical Product Truth

Source documents reviewed:

- `Claire_Syntalion_Unified_Platform_Definition_v1.docx`
- `Lifecycle Spine.txt`
- `Final Endgame Pipeline.txt`
- `Full Breakthrough-to-Acquisition Package Pipeline.txt`
- related branch/governance/pipeline files under `Docs Main/pipelines`

Established truth:

- Claire is a governed lifecycle intelligence platform.
- The 30-stage lifecycle is the canonical execution spine.
- Portfolio and acquisition intelligence are primary early routes.
- Breakthrough escalation is conditional and governed.
- Hybrid mode is the maximum capability state: deterministic reasoning plus live intelligence fusion.
- Dashboard/cockpit is an operational command surface, not a static UI.
- Unsafe autonomy, body reads, automatic updates, runtime mutation, and browser execution must remain blocked until explicit governance gates are satisfied.

## Current Operational State

Most recent implementation area:

- Dashboard v3 / endpoint-mapped final operator dashboard.
- Legacy dashboard bridge assets.
- Active-control map and operator action bridge.

Current implementation signals:

- `claire/app.py` now owns `/dashboard`, `/dashboard/v3`, `/operator-dashboard`, `/operator-cockpit`, `/command-center`, `/dashboard/endpoint-map`, and `/dashboard/v3/assets/{asset_name}`.
- Dashboard v3 files exist under `frontend/command_center/modern`.
- Endpoint map exists at `output/dashboard_endpoint_map/dashboard_endpoint_map_latest.json` and declares 595 mapped endpoints.
- The launcher still opens `frontend/cockpit/shell/cockpit_shell.html`, which is not the freshest dashboard v3 surface. This is a visible demo mismatch.

## Installer Findings

Root installers found:

- `install_claire_v19_89_8_s1293_audit_route_mount_repair.py`
- `install_claire_v19_89_8_s1294_direct_create_app_audit_route_mount_repair.py`
- `install_claire_v19_89_8_s1295_s1322_system_vs_dashboard_operation_gap_audit.py`
- `install_claire_v19_89_8_s1323_s1350_dashboard_active_control_map.py`
- `install_claire_v19_89_8_s1351_s1450_system_fit_operator_cockpit_v2.py`
- `install_claire_v19_89_8_s1351_s1450_system_fit_operator_cockpit_v2_FIXED.py`
- `install_claire_v19_89_8_s1476_s1500_project_cleanout_audit.py`
- `install_claire_v19_89_8_s1501_s1600_endpoint_mapped_final_operator_dashboard_v3.py`
- `install_claire_v19_89_8_s1626_s1650_dashboard_v3_legacy_contract_bridge.py`

Syntax check:

- 8 of 9 root installers compile.
- `install_claire_v19_89_8_s1351_s1450_system_fit_operator_cockpit_v2.py` fails with an unterminated string literal at line 1516.
- The `_FIXED` variant compiles and appears to repair that assertion.

Acquisition implication:

- Root installers must be consolidated into a single canonical installer or archived as historical repair packs.
- Broken installer variants cannot remain in the project root for diligence.

## Repository Pollution Findings

High-impact pollution:

- `exports`: approximately 36,119 files.
- backup-style files: approximately 398.
- `.pyc` files: approximately 2,460.
- project root contains installer scripts, launcher backups, version backups, audit outputs, runtime outputs, reports, archive trees, and current source.
- `git status` shows massive deleted/modified/untracked state, making provenance and review difficult.
- `README.md` is deleted in git status while `pyproject.toml` still declares it as the project readme.
- `.env` exists in the root and must be treated as sensitive.

Acquisition implication:

- The project should be split into a clean product repository plus a separate evidence/archive package.
- The current root is not suitable for a buyer, investor, or technical diligence reviewer as-is.

## Live Web Connectivity Boundary

The codebase contains extensive governed live-web infrastructure, including provider readiness, metadata probes, live search dashboard smoke tests, body-read gates, review queues, and real-provider probe routes.

Current governance posture found in `claire/app.py` and governed web modules:

- live probe registered but blocked by default.
- required env gates include `CLAIRE_ALLOW_GOVERNED_LIVE_METADATA_PROBE` and `CLAIRE_ALLOW_HEAD_ONLY_PROBE`.
- body read, runtime truth mutation, autonomous execution, browser execution, and automatic updates are explicitly blocked in the default path.
- `/api/governed/live-probe/status` is GET.
- `/api/governed/live-probe/head` is POST but requires explicit operator acknowledgement and one-shot intent before local acceptance.

Acquisition implication:

- This is the right safety posture for a pre-live system.
- Before acquirer demo, live-web mode should be presented as "governed controlled connectivity, blocked by default" with one controlled proof path.

## Critical Blockers Before Acquisition Demo

1. Clean launcher/demo path.
   The launcher opens an older cockpit shell while active dashboard v3 lives elsewhere.

2. Reproducible environment.
   Local `.venv` is missing here, Windows `py` has no installed Python behind it, and bundled Python lacks `fastapi` and `pytest`. Full runtime verification is blocked until a real env is restored.

3. Installer authority.
   Multiple staged installers exist at root and one is broken. A canonical installer must be selected.

4. Repository hygiene.
   Output/archive/proof files swamp the source tree. The root should not carry 36k export files and thousands of bytecode artifacts.

5. Acquisition narrative.
   The product definition is strong, but the repo does not yet tell the same story cleanly. The buyer-facing package needs an executive overview, architecture map, controlled demo script, governance proof, and acquisition-use-case examples.

## Recommended Next Sequence

1. Freeze the current working state.
   Create a timestamped archive or branch before cleanup.

2. Create a clean acquisition branch.
   Keep source, tests, frontend, docs, requirements, launcher, and selected proof artifacts.

3. Quarantine root pollution.
   Move old installers, backup variants, output dumps, bytecode, archive trees, and giant exports out of the product root.

4. Canonicalize launch.
   Make the launcher open the active `/dashboard` or `/dashboard/v3` route served by `main.py`, not an older static shell.

5. Canonicalize installer.
   Preserve the latest valid dashboard v3 installer and retire broken or superseded variants.

6. Restore test runtime.
   Rebuild `.venv`, install requirements, and run targeted dashboard/live-governance tests.

7. Build acquisition package.
   Package: platform definition, lifecycle spine, dashboard screenshots, governed live-web boundary, acquisition intelligence examples, and technical diligence notes.

## Questions To Resolve

1. Should the acquirer-facing demo emphasize portfolio/acquisition intelligence first, or governed live-web activation first?
2. Should the clean branch keep historical installers as `docs/proof/installers`, or move them outside the repository entirely?
3. Is the intended buyer strategic acquirer, technical diligence partner, investor, or first enterprise pilot customer?
4. Should live web be shown as blocked-by-default only, or should we prepare one controlled HEAD-only live proof?
5. Which dashboard is canonical for demo: endpoint-mapped v3 or the cockpit shell?
