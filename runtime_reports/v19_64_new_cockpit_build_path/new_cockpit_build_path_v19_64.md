# Claire Syntalion v19.64
## New Cockpit Build Path From Existing Systems

Generated: 2026-05-11T09:28:48.103288Z

## Decision

Map-complete enough to define cockpit build path; implementation should begin only after this blueprint is reviewed.

## New Cockpit Root

`frontend/cockpit/`

## Source-of-Truth Rule

Backend runtime APIs and canonical payload contracts own truth. Frontend owns presentation, navigation, command entry, and operator interaction.

## Required Folder Architecture

### `frontend/cockpit/shell/`
- Purpose: application shell, workspace layout, navigation, docking, route state, panel registry
- First files to create later:
  - `frontend/cockpit/shell/cockpit_shell.html`
  - `frontend/cockpit/shell/cockpit_shell.css`
  - `frontend/cockpit/shell/cockpit_bootstrap.js`
  - `frontend/cockpit/shell/workspace_manager.js`
  - `frontend/cockpit/shell/panel_registry.js`
  - `frontend/cockpit/shell/route_state.js`

### `frontend/cockpit/shared/`
- Purpose: shared adapters, API client, payload adapter, state store, formatters, error states
- First files to create later:
  - `frontend/cockpit/shared/api_client.js`
  - `frontend/cockpit/shared/payload_adapter.js`
  - `frontend/cockpit/shared/state_store.js`
  - `frontend/cockpit/shared/status_model.js`
  - `frontend/cockpit/shared/empty_state.js`

### `frontend/cockpit/runtime/`
- Purpose: runtime status, active lifecycle, execution graph, run history, runtime truth, evidence queue
- First files to create later:
  - `frontend/cockpit/runtime/runtime_panel.js`
  - `frontend/cockpit/runtime/lifecycle_panel.js`
  - `frontend/cockpit/runtime/execution_graph_panel.js`
  - `frontend/cockpit/runtime/run_history_panel.js`
  - `frontend/cockpit/runtime/runtime_truth_panel.js`
  - `frontend/cockpit/runtime/evidence_queue_panel.js`

### `frontend/cockpit/intelligence/`
- Purpose: permanent search command surface, governed web, discovery, trend, portfolio, signals
- First files to create later:
  - `frontend/cockpit/intelligence/command_surface.js`
  - `frontend/cockpit/intelligence/search_panel.js`
  - `frontend/cockpit/intelligence/governed_web_panel.js`
  - `frontend/cockpit/intelligence/discovery_panel.js`
  - `frontend/cockpit/intelligence/trend_panel.js`
  - `frontend/cockpit/intelligence/portfolio_panel.js`
  - `frontend/cockpit/intelligence/signals_panel.js`

### `frontend/cockpit/design/`
- Purpose: breakthroughs, advancement path, AutoDesign, blueprint viewer, validation, buildability
- First files to create later:
  - `frontend/cockpit/design/breakthrough_panel.js`
  - `frontend/cockpit/design/advancement_path_panel.js`
  - `frontend/cockpit/design/autodesign_panel.js`
  - `frontend/cockpit/design/blueprint_viewer_panel.js`
  - `frontend/cockpit/design/validation_panel.js`
  - `frontend/cockpit/design/buildability_panel.js`

### `frontend/cockpit/package/`
- Purpose: packages, acquisition fit, strategic positioning, exports
- First files to create later:
  - `frontend/cockpit/package/packages_panel.js`
  - `frontend/cockpit/package/acquisition_fit_panel.js`
  - `frontend/cockpit/package/positioning_panel.js`
  - `frontend/cockpit/package/exports_panel.js`

### `frontend/cockpit/system/`
- Purpose: system health, backend status, route proof, provider readiness, governance proof
- First files to create later:
  - `frontend/cockpit/system/system_health_panel.js`
  - `frontend/cockpit/system/route_proof_panel.js`
  - `frontend/cockpit/system/provider_readiness_panel.js`
  - `frontend/cockpit/system/governance_panel.js`

## Build Sequence

### v19.65 — Cockpit Root + Legacy Dashboard Freeze Marker
- Purpose: Create frontend/cockpit skeleton and mark old dashboard as legacy reference without deleting it.
- Runtime change: none/minimal
- Must include:
  - README/contract marker
  - legacy reference note
  - no fetch behavior yet

### v19.66 — Cockpit Shell + Workspace Manager
- Purpose: Create stable shell, layout, navigation, workspace manager, and panel registry.
- Runtime change: frontend only
- Must include:
  - panel registry
  - route state
  - empty states
  - system status placeholder

### v19.67 — Shared API Client + Canonical Payload Adapter
- Purpose: Create the single frontend adapter for /dashboard/payload and /dashboard/payload/status.
- Runtime change: frontend fetch consolidation only
- Must include:
  - api_client.js
  - payload_adapter.js
  - error handling
  - offline/blocked states

### v19.68 — Permanent Search Command Surface
- Purpose: Build search panel as command/search/research surface from the start.
- Runtime change: frontend integration with existing search/provider routes
- Must include:
  - normal web search mode
  - governed research mode
  - runtime/project search mode
  - command recognition placeholder

### v19.69 — Runtime + Lifecycle Panels
- Purpose: Render active runtime state, 30-stage lifecycle, run history, terminal states, runtime truth/evidence.
- Runtime change: consume existing payload/runtime APIs
- Must include:
  - runtime status
  - lifecycle graph/list
  - run history
  - evidence/runtime truth

### v19.70 — Intelligence Workspace
- Purpose: Render governed web, discovery, trends, portfolio, signals.
- Runtime change: consume existing payload/search/governed web APIs
- Must include:
  - governed web status
  - discovery
  - trends
  - portfolio
  - signals

### v19.71 — Design + Breakthrough Workspace
- Purpose: Render breakthrough, advancement path, AutoDesign, Design Portal/blueprints, validation/buildability.
- Runtime change: consume existing payload/design route outputs where available
- Must include:
  - breakthroughs
  - advancement path
  - AutoDesign
  - blueprint viewer
  - validation

### v19.72 — Package + Export Workspace
- Purpose: Render package, acquisition fit, positioning, exports.
- Runtime change: consume existing payload/package outputs
- Must include:
  - packages
  - acquisition fit
  - positioning
  - exports

### v19.73 — Cockpit Parity Gate
- Purpose: Compare old dashboard against new cockpit and prove payload/runtime/search parity before retirement.
- Runtime change: test/report only
- Must include:
  - parity report
  - legacy dashboard retirement readiness
  - missing coverage list

## Non-Negotiable Constraints

- Do not scale the old dashboard.
- Do not delete legacy dashboard until parity is proven.
- Do not add new cockpit panels without registering them in panel registry.
- Do not create more than one canonical payload fetch owner.
- Do not build search without governed web/source-trust awareness.
- Do not let UI become the source of runtime truth.
- Do not redesign cockpit again after v19.65+ without a failed parity reason.
