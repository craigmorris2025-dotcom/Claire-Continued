# Claire v19.84.6 Critical Route Consolidation Plan

- Generated: `2026-05-13T11:22:15.629711+00:00`
- Status: `consolidation_required`
- Read-only: `True`
- Backend owns truth: `True`
- Cockpit owns presentation only: `True`

## Summary

- `critical_route_count`: `6`
- `passing_critical_routes`: `0`
- `failing_critical_routes`: `6`
- `duplicate_failures`: `6`
- `missing_failures`: `0`

## Required Actions

### `GET /dashboard/payload`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.enterprise_cockpit_payload_bridge`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.dashboard_payload_bridge.get_dashboard_payload`
  - `claire.api.routes_enterprise_cockpit_payload.dashboard_payload`
  - `claire.routes.authored_cockpit_compat_routes.authored_dashboard_payload`

### `GET /dashboard/payload/status`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.enterprise_cockpit_payload_status`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.dashboard_payload_bridge.get_dashboard_payload_status`
  - `claire.api.routes_enterprise_cockpit_payload.dashboard_payload_status`
  - `claire.routes.authored_cockpit_payload_binding_routes.dashboard_payload_status`

### `POST /runs/start`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.enterprise_runtime_runs_backend`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.routes_enterprise_runs.start_run`
  - `claire.routes.authored_cockpit_compat_routes.authored_start_run`

### `GET /runtime/continuous/review-queue`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.continuous_intelligence_review_queue`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.routes_continuous_runtime.continuous_review_queue`
  - `claire.routes.authored_cockpit_compat_routes.authored_review_queue`

### `GET /runtime/continuous/status`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.continuous_intelligence_runtime_status`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.routes_continuous_runtime.continuous_status`
  - `claire.routes.authored_cockpit_compat_routes.authored_continuous_status`

### `GET /universes`
- Failure: `duplicate_route_owner`
- Canonical owner: `backend.source_universe_backend`
- Action: `demote_duplicate_owners`
- Required change: Keep one canonical backend owner. Convert all noncanonical owners to delegated helpers, rename duplicate paths, or remove their router mount from create_app.
- Safety rule: Do not change payload schema or cockpit fetch route.
- Owners seen:
  - `claire.api.routes_source_universes.universes`
  - `claire.routes.authored_cockpit_compat_routes.authored_universes`

## Recommendation

Do not proceed to cockpit binding lock until critical route failures are resolved.

Next build: `v19.84.7 Critical Route Owner Demotion`
