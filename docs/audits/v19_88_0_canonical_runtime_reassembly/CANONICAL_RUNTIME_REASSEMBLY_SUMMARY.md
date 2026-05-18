# Claire v19.88.0 Canonical Runtime Reassembly Map

Generated: 2026-05-13T03:34:13.558827+00:00

## Policy
- audit_only: **True**
- mutated_files: **False**
- mounted_routes: **False**
- rewired_dashboard: **False**
- enabled_live_internet: **False**
- runtime_truth_mutated: **False**

## Live Interpretation
**server_not_running_or_port_refused_during_audit**

## Counts
- app_factories: **38**
- router_objects: **71**
- include_router_calls: **525**
- python_route_hits: **339**
- unique_static_route_paths: **207**
- frontend_endpoint_refs: **22122**
- unique_frontend_paths: **497**
- launcher_refs: **4156**
- live_openapi_paths: **0**

## Missing Required Operational Endpoints
- `/`
- `/health`
- `/docs`
- `/openapi.json`
- `/dashboard/payload/status`
- `/dashboard/payload`
- `/api/dashboard/search/provider/status`
- `/api/dashboard/search/provider/probe`
- `/api/dashboard/search/live`
- `/api/dashboard/search/smoke/google`

## Next Repair Order
- If server_not_running_or_port_refused_during_audit, start python main.py and rerun the audit before repairing routes.
- Lock canonical startup: main.py -> claire.app:create_app.
- Lock one canonical router registry.
- Mount /health, /docs, /openapi.json.
- Mount /dashboard/payload/status and /dashboard/payload.
- Mount governed search provider/status/probe/live routes.
- Mount live source catalog/source universe routes.
- Mount continuous runtime status routes.
- Bind cockpit status cards to canonical endpoints.
- Then prove live source catalog -> governed probe -> evidence -> runtime -> cockpit.
