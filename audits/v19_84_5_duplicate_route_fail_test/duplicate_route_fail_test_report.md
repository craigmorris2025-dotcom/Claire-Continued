# Claire v19.84.5 Duplicate Route Fail Test

- Generated: `2026-05-13T11:22:15.614711+00:00`
- Status: `failed`
- Mounted route count: `69`
- Passing critical route keys: `0`
- Failing critical route keys: `6`

## Failures

- `GET /dashboard/payload` — `duplicate_route_owner` owner_count=`3`
  - `claire.api.dashboard_payload_bridge.get_dashboard_payload`
  - `claire.api.routes_enterprise_cockpit_payload.dashboard_payload`
  - `claire.routes.authored_cockpit_compat_routes.authored_dashboard_payload`
- `GET /dashboard/payload/status` — `duplicate_route_owner` owner_count=`3`
  - `claire.api.dashboard_payload_bridge.get_dashboard_payload_status`
  - `claire.api.routes_enterprise_cockpit_payload.dashboard_payload_status`
  - `claire.routes.authored_cockpit_payload_binding_routes.dashboard_payload_status`
- `POST /runs/start` — `duplicate_route_owner` owner_count=`2`
  - `claire.api.routes_enterprise_runs.start_run`
  - `claire.routes.authored_cockpit_compat_routes.authored_start_run`
- `GET /runtime/continuous/review-queue` — `duplicate_route_owner` owner_count=`2`
  - `claire.api.routes_continuous_runtime.continuous_review_queue`
  - `claire.routes.authored_cockpit_compat_routes.authored_review_queue`
- `GET /runtime/continuous/status` — `duplicate_route_owner` owner_count=`2`
  - `claire.api.routes_continuous_runtime.continuous_status`
  - `claire.routes.authored_cockpit_compat_routes.authored_continuous_status`
- `GET /universes` — `duplicate_route_owner` owner_count=`2`
  - `claire.api.routes_source_universes.universes`
  - `claire.routes.authored_cockpit_compat_routes.authored_universes`

## Passing Critical Routes


## Next Build

If this report fails, v19.84.6 must demote duplicate owners or restore missing critical routes before cockpit binding work proceeds.
