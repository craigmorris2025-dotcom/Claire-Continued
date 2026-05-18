# Cockpit Frontend Input Map v19.63

Generated: 2026-05-11T09:25:08.720576Z

- New cockpit root: `frontend/cockpit/`
- Legacy dashboard rule: Do not scale the existing dashboard. Treat it as reference until parity is proven.
- Source-of-truth rule: Frontend owns presentation and operator interaction only. Backend payload/routes own truth.

## Required New Frontend Modules

### shell
- Path: `frontend/cockpit/shell/`
- Purpose: workspace, navigation, docking, panel registry, route state

### shared_payload_adapter
- Path: `frontend/cockpit/shared/`
- Purpose: single fetch owner for /dashboard/payload and status

### search_command_surface
- Path: `frontend/cockpit/intelligence/`
- Purpose: permanent search/command/research/agent surface

### runtime_panels
- Path: `frontend/cockpit/runtime/`
- Purpose: runtime status, lifecycle execution, run history, evidence/runtime truth

### governed_web_workspace
- Path: `frontend/cockpit/intelligence/`
- Purpose: governed web/search operations, provider status, trust/rate/allowlist visibility

## No-Redesign-Later Constraints

- Permanent search command surface must be top-level from the start.
- Panel registry must exist before adding panels.
- Payload adapter must be the only canonical dashboard payload fetch owner.
- Legacy dashboard shells must not become new cockpit architecture by accident.
- Cockpit must reserve spaces for runtime, intelligence, design, package, and system health from the start.
