# Claire Dashboard Functional Surface

## Purpose

Claire's dashboard is now treated as a lifecycle execution command center, not as a generic analysis page. The current tab scaffold is:

- Run
- Discover
- Trend
- Portfolio
- Breakthrough
- Design
- Packages
- Monitor
- System

The visual shell is intentionally still a functional scaffold. Final polish is deferred until the tabs are reliably connected to route-aware output.

## Data Sources

- `core_run_output.json`: primary product output for user-facing tabs.
- `run_history.json`: lightweight run index and history list only.
- `full_pipeline_output.json` / raw JSON: loaded only on demand from System / Raw / Debug surfaces.

## Tab Responsibilities

### Run

Command / launch surface. Shows run type, mode, universe/domain/buyer selectors, objective/command selector, signal/project input, launch controls, active route badge, current status, terminal state, scan iteration count, and whether review is required.

Empty state: waiting for run.

### Discover

Discovery output surface. Shows signal basis, governed signal count, discovery result, gap qualification/reason, discovery confidence, missing data, and next action.

Empty state: waiting for scan result or missing `core_run_output.json`.

### Trend

Root trend/thesis surface. Shows trend name, trend stage, why now, supporting signals, momentum, thesis, affected themes/entities, confidence, and next action.

Empty state: trend not discovered yet.

### Portfolio

Portfolio creation / optimization surface. Shows portfolio thesis, portfolio logic, included opportunities/themes, priority ranking, exposure notes, risk notes, recommended action, and confidence.

Empty state: no portfolio output produced for this route, with reason shown.

### Breakthrough

Breakthrough classification surface. Shows breakthrough detected yes/no, primary/secondary types, trigger signals, rationale, why triggered or not triggered, route recommendation, and confidence context.

Empty state: breakthrough not triggered.

### Design

AutoDesign, Design Portal, and Technology Intelligence surface. Shows route-aware skip/trigger state, design concept, components, dependencies, selected technologies/stack, architecture summary, blueprint/spec summary, implementation phases, validation status, and technology intelligence notes.

Empty state: AutoDesign/Design Portal/Technology Intelligence skipped by route.

### Packages

Final package and acquisition surface. Shows package availability, summary, market positioning, moat/differentiation, business model/value capture, acquirer target count, acquisition readiness, risks/objections, export path, and run history/output browser.

Empty state: package not available yet.

### Monitor

Live run monitoring surface. Shows selected-run scan iteration progress, current scan pass, last run status, terminal state, last export status, run history count, selected run, export path, and known errors.

Empty state: no active scan selected.

### System

Lifecycle proof and system health surface. Shows 30-stage lifecycle status, skipped/failed/insufficient stages, completion gate, core output contract, health summary, and raw/debug JSON on demand only.

Empty state: no lifecycle/core output loaded.

## Route Behavior

The dashboard does not imply that every route should produce design, breakthrough, portfolio, or acquisition output. Each functional tab answers:

- What Claire produced for this function.
- Whether the function was triggered.
- If skipped, why.
- If blocked, what data is missing.
- What the user should review next.

## Validation Results

2026-05-02 focused validation:

- `node --check src/frontend/export_dashboard/dashboard.js`: passed.
- Duplicate HTML ID check for `src/frontend/export_dashboard/index.html`: passed, no duplicates returned.
- Targeted Python syntax check for `src/claire/output/core_output_builder.py` and `tools/serve_export_dashboard.py`: passed.
- `Invoke-WebRequest http://127.0.0.1:8765`: passed, HTTP 200.
- Headless Edge DOM load check: passed for the new functional tabs and Design/Technology surfaces.

Console inspection was not completed because the local Node REPL does not have Playwright installed. No backend blocking error was observed during the focused checks.
