# Claire v19.84.3 Canonical Route Mount Audit

- Generated: `2026-05-13T11:22:15.068710+00:00`
- Status: `ok`
- Mounted route count: `69`
- Duplicate mounted route keys: `8`

## Critical Route Status

| Route | State | Owner Count |
|---|---:|---:|
| `/dashboard/payload` | `duplicate_owner` | `3` |
| `/dashboard/payload/status` | `duplicate_owner` | `3` |
| `/runtime/continuous/status` | `duplicate_owner` | `2` |
| `/runtime/continuous/review-queue` | `duplicate_owner` | `2` |
| `/runs/start` | `duplicate_owner` | `2` |
| `/universes` | `duplicate_owner` | `2` |

## Duplicate Mounted Routes

### `GET /dashboard/payload`
- `claire.api.dashboard_payload_bridge.get_dashboard_payload` via `APIRoute`
- `claire.api.routes_enterprise_cockpit_payload.dashboard_payload` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_dashboard_payload` via `APIRoute`

### `GET /dashboard/payload/status`
- `claire.api.dashboard_payload_bridge.get_dashboard_payload_status` via `APIRoute`
- `claire.api.routes_enterprise_cockpit_payload.dashboard_payload_status` via `APIRoute`
- `claire.routes.authored_cockpit_payload_binding_routes.dashboard_payload_status` via `APIRoute`

### `POST /runs/start`
- `claire.api.routes_enterprise_runs.start_run` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_start_run` via `APIRoute`

### `POST /runtime/continuous/pause`
- `claire.api.routes_continuous_runtime.continuous_pause` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_continuous_pause` via `APIRoute`

### `GET /runtime/continuous/review-queue`
- `claire.api.routes_continuous_runtime.continuous_review_queue` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_review_queue` via `APIRoute`

### `POST /runtime/continuous/start`
- `claire.api.routes_continuous_runtime.continuous_start` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_continuous_start` via `APIRoute`

### `GET /runtime/continuous/status`
- `claire.api.routes_continuous_runtime.continuous_status` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_continuous_status` via `APIRoute`

### `GET /universes`
- `claire.api.routes_source_universes.universes` via `APIRoute`
- `claire.routes.authored_cockpit_compat_routes.authored_universes` via `APIRoute`

## Cockpit Endpoint Dependencies

- Frontend endpoint references found: `123`

- `/api/dashboard/payload` in `frontend\cockpit\shared\canonical_payload_adapter.js` line `8`
- `/api/dashboard/payload` in `frontend\cockpit\shell\assets\claire_authored_enterprise_cockpit_shell.js` line `161`
- `/api/dashboard/payload/status` in `frontend\cockpit\shared\canonical_payload_adapter.js` line `10`
- `/api/dashboard/search/live` in `frontend\command_center\modern\assets\js\claire_v18_74_dashboard_live_web_search_final_binding.js` line `6`
- `/api/dashboard/search/live` in `frontend\command_center\modern\assets\js\claire_v18_74_dashboard_live_web_search_final_binding.js` line `70`
- `/api/dashboard/search/live` in `frontend\command_center\modern\dashboard_primary_web_search_binding.js` line `6`
- `/api/dashboard/search/live` in `frontend\command_center\modern\governed_live_search_ui_binding.js` line `4`
- `/api/dashboard/search/live` in `frontend\command_center\modern\index.html` line `9`
- `/api/dashboard/search/live` in `frontend\command_center\modern\index.html` line `10`
- `/api/dashboard/search/live` in `frontend\command_center\modern\operator_dashboard.js` line `301`
- `/api/dashboard/search/live` in `frontend\command_center\modern\operator_dashboard.js` line `318`
- `/api/dashboard/search/live` in `frontend\command_center\modern\operator_dashboard.js` line `335`
- `/api/dashboard/search/live` in `frontend\command_center\modern\operator_dashboard.js` line `352`
- `/api/dashboard/search/live` in `frontend\command_center\modern\operator_dashboard.js` line `369`
- `/api/dashboard/search/provider/probe` in `frontend\command_center\modern\governed_provider_probe_ui_binding.js` line `5`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\assets\js\claire_v18_74_dashboard_live_web_search_final_binding.js` line `7`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\governed_provider_probe_ui_binding.js` line `4`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\operator_dashboard.js` line `302`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\operator_dashboard.js` line `319`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\operator_dashboard.js` line `336`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\operator_dashboard.js` line `353`
- `/api/dashboard/search/provider/status` in `frontend\command_center\modern\operator_dashboard.js` line `370`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\assets\js\claire_v18_74_dashboard_live_web_search_final_binding.js` line `8`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\dashboard_primary_web_search_binding.js` line `7`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\operator_dashboard.js` line `303`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\operator_dashboard.js` line `320`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\operator_dashboard.js` line `337`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\operator_dashboard.js` line `354`
- `/api/dashboard/search/smoke/google` in `frontend\command_center\modern\operator_dashboard.js` line `371`
- `/api/dashboard/state` in `frontend\command_center\modern\claire_functional_operator_dashboard.js` line `1`
- `/api/dashboard/state` in `frontend\command_center\modern\claire_single_screen_operator.js` line `5`
- `/api/dashboard/state` in `frontend\command_center\modern\modern_dashboard.js` line `1`
- `/api/dashboard/state` in `frontend\command_center\modern\operator_dashboard.js` line `10`
- `/api/dashboard/state` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/api/dashboard/system-status` in `frontend\export_dashboard\dashboard.js` line `1143`
- `/api/health` in `frontend\export_dashboard\dashboard.js` line `14`
- `/api/health` in `frontend\export_dashboard\dashboard.js` line `1192`
- `/api/internet/campaigns` in `frontend\command_center\modern\operator_dashboard.js` line `13`
- `/api/internet/campaigns` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/api/internet/source-trust` in `frontend\command_center\modern\operator_dashboard.js` line `12`
- `/api/internet/source-trust` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/api/launch/regression-lock` in `frontend\command_center\modern\claire_single_screen_operator.js` line `11`
- `/api/launch/regression-lock` in `frontend\command_center\modern\operator_dashboard.js` line `11`
- `/api/launch/regression-lock` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/api/runs` in `frontend\export_dashboard\dashboard.js` line `818`
- `/api/runtime/latest` in `frontend\command_center\modern\claire_operating_environment.js` line `1069`
- `/api/runtime/state` in `frontend\command_center\modern\claire_single_screen_operator.js` line `6`
- `/dashboard/alignment/buttons` in `frontend\claire_dashboard_actions.js` line `9`
- `/dashboard/alignment/capabilities` in `frontend\claire_dashboard_actions.js` line `14`
- `/dashboard/alignment/status` in `frontend\claire_dashboard_actions.js` line `13`
- `/dashboard/alignment/status` in `frontend\command_center\modern\claire_single_screen_operator.js` line `5`
- `/dashboard/payload` in `frontend\cockpit\assets\enterprise_cockpit_workspace_shell.js` line `258`
- `/dashboard/payload` in `frontend\cockpit\runtime\runtime_payload_gate.js` line `48`
- `/dashboard/payload` in `frontend\cockpit\shared\canonical_payload_adapter.js` line `7`
- `/dashboard/payload` in `frontend\cockpit\shared\payload_adapter.js` line `6`
- `/dashboard/payload` in `frontend\cockpit\shared\payload_route_guard.js` line `15`
- `/dashboard/payload` in `frontend\cockpit\shell\assets\claire_authored_enterprise_cockpit_shell.js` line `161`
- `/dashboard/payload` in `frontend\cockpit\shell\assets\claire_discovery_candidate_surface.js` line `185`
- `/dashboard/payload` in `frontend\command_center\modern\claire_dashboard_payload_bridge.js` line `8`
- `/dashboard/payload/status` in `frontend\cockpit\assets\enterprise_cockpit_workspace_shell.js` line `249`
- `/dashboard/payload/status` in `frontend\cockpit\shared\canonical_payload_adapter.js` line `9`
- `/dashboard/payload/status` in `frontend\cockpit\shared\payload_adapter.js` line `5`
- `/dashboard/payload/status` in `frontend\cockpit\shared\payload_route_guard.js` line `14`
- `/dashboard/state` in `frontend\command_center\modern\claire_connected_operator_dashboard.js` line `5`
- `/dashboard/state` in `frontend\command_center\modern\claire_functional_operator_dashboard.js` line `1`
- `/dashboard/state` in `frontend\command_center\modern\claire_single_screen_operator.js` line `5`
- `/dashboard/state` in `frontend\command_center\modern\claire_workspace_agent_dashboard.js` line `5`
- `/dashboard/state` in `frontend\command_center\modern\operator_dashboard.js` line `10`
- `/dashboard/state` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/dashboard/state` in `frontend\command_center\modern\product_dashboard.js` line `38`
- `/health` in `frontend\claire_dashboard_actions.js` line `12`
- `/health` in `frontend\command_center\modern\claire_single_screen_operator.js` line `4`
- `/health` in `frontend\command_center\modern\operator_dashboard.js` line `8`
- `/health` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/health` in `frontend\command_center\modern\product_dashboard.js` line `38`
- `/internet/campaigns` in `frontend\command_center\modern\claire_single_screen_operator.js` line `9`
- `/internet/campaigns` in `frontend\command_center\modern\operator_dashboard.js` line `13`
- `/internet/campaigns` in `frontend\command_center\modern\product_dashboard.js` line `13`
- `/internet/campaigns` in `frontend\command_center\modern\product_dashboard.js` line `38`
- `/internet/campaigns/status` in `frontend\command_center\modern\claire_single_screen_operator.js` line `9`
- ... 43 more references omitted; see JSON report.

## Recommendations

- **critical** `critical_route` `/dashboard/payload` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `critical_route` `/dashboard/payload/status` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `critical_route` `/runtime/continuous/status` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `critical_route` `/runtime/continuous/review-queue` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `critical_route` `/runs/start` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `critical_route` `/universes` — Duplicate owners detected. v19.84.4 must assign one canonical owner and demote all others.
- **critical** `route_registry` `*` — Duplicate method/path route keys exist. Add enforcement before runtime/cockpit expansion.

## Next Build

v19.84.4 should create the Canonical Route Owner Registry using this audit as evidence.
