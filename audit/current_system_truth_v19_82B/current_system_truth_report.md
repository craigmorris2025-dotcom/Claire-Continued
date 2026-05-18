# Claire Current System Truth Report v19.82B

Generated UTC: 2026-05-11T20:59:36.345697+00:00
Project root: `C:\Users\craig\OneDrive\Desktop\Claire`

## Summary

- Manifest entries: 9845
- Python route hits: 287
- Frontend cockpit/dashboard files of interest: 22
- Payload-related files: 692
- Launcher candidates: 4
- Build artifacts found: 13

## App Candidates

- `main.py`
- `claire/app.py`

## Critical Route Hits

- `GET` `/operator/dashboard/state` in `claire/api/operator_dashboard_compat_routes.py`
- `GET` `/runtime/continuous/status` in `claire/api/routes_continuous_runtime.py`
- `POST` `/runtime/continuous/start` in `claire/api/routes_continuous_runtime.py`
- `POST` `/runtime/continuous/pause` in `claire/api/routes_continuous_runtime.py`
- `GET` `/runtime/continuous/cycles` in `claire/api/routes_continuous_runtime.py`
- `GET` `/runtime/continuous/review-queue` in `claire/api/routes_continuous_runtime.py`
- `GET` `/dashboard/payload` in `claire/api/routes_enterprise_cockpit_payload.py`
- `GET` `/dashboard/payload/status` in `claire/api/routes_enterprise_cockpit_payload.py`
- `POST` `/runs/start` in `claire/api/routes_enterprise_runs.py`
- `GET` `/runs/latest` in `claire/api/routes_enterprise_runs.py`
- `GET` `/runs/{run_id}/status` in `claire/api/routes_enterprise_runs.py`
- `GET` `/runs/{run_id}/lifecycle` in `claire/api/routes_enterprise_runs.py`
- `GET` `/runs/{run_id}/gates` in `claire/api/routes_enterprise_runs.py`
- `GET` `/runs/{run_id}/missing-evidence` in `claire/api/routes_enterprise_runs.py`
- `POST` `/runs/{run_id}/enrich` in `claire/api/routes_enterprise_runs.py`
- `GET` `/search/dashboard-smoke` in `claire/api/routes_live_search_dashboard_smoke.py`
- `GET` `/operator/dashboard/state` in `claire/api/routes_operator_dashboard.py`
- `GET` `/dashboard/state` in `claire/api/routes_operator_dashboard.py`
- `GET` `/api/dashboard/state` in `claire/api/routes_operator_dashboard.py`
- `GET` `/operator/dashboard/summary` in `claire/api/routes_operator_dashboard.py`
- `POST` `/operator/dashboard/refresh` in `claire/api/routes_operator_dashboard.py`
- `GET` `/runtime/truth` in `claire/api/routes_runtime_truth.py`
- `GET` `/runtime/state` in `claire/api/routes_runtime_truth.py`
- `POST` `/runtime/truth/rebuild` in `claire/api/routes_runtime_truth.py`
- `GET` `/dashboard/runtime-truth` in `claire/api/routes_runtime_truth.py`
- `GET` `/universes` in `claire/api/routes_source_universes.py`
- `GET` `/universes/{universe_id}` in `claire/api/routes_source_universes.py`
- `POST` `/universes/{universe_id}/probe` in `claire/api/routes_source_universes.py`
- `POST` `/dashboard` in `claire/api/search_bar_dashboard_api.py`
- `GET` `/dashboard` in `claire/internet_operations_dashboard/api_routes.py`
- `POST` `/dashboard` in `claire/internet_runtime_integration/api_routes.py`
- `GET` `/dashboard/payload` in `claire/routes/authored_cockpit_compat_routes.py`
- `GET` `/runtime/continuous/status` in `claire/routes/authored_cockpit_compat_routes.py`
- `POST` `/runtime/continuous/start` in `claire/routes/authored_cockpit_compat_routes.py`
- `POST` `/runtime/continuous/pause` in `claire/routes/authored_cockpit_compat_routes.py`
- `GET` `/runtime/continuous/review-queue` in `claire/routes/authored_cockpit_compat_routes.py`
- `GET` `/universes` in `claire/routes/authored_cockpit_compat_routes.py`
- `POST` `/runs/start` in `claire/routes/authored_cockpit_compat_routes.py`
- `GET` `/dashboard/payload/status` in `claire/routes/authored_cockpit_payload_binding_routes.py`
- `GET` `/api/dashboard/payload` in `claire/routes/authored_cockpit_payload_binding_routes.py`
- `GET` `/api/dashboard/payload/status` in `claire/routes/authored_cockpit_payload_binding_routes.py`

## Frontend Fetch References

- `../cockpit_autonomous_lifecycle_contract.json` in `frontend/cockpit/runtime/autonomous_lifecycle_graph.js`
- `/api/command` in `frontend/js/api.js`
- `/api/platform/status` in `frontend/js/platform.js`
- `/api/platform/resolve` in `frontend/js/platform.js`

## Launcher Candidates

- `LAUNCH_CLAIRE.bat`
- `audit_claire_current_system_truth_v19_82B.py`
- `main.py`
- `safe_install_claire_version.py`

## Next Use

Send back `audit/current_system_truth_v19_82B/current_system_truth_report.md` first.
If needed, also send `python_route_audit.json`, `frontend_cockpit_audit.json`, and `dashboard_payload_audit.json`.
