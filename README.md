# Claire Syntalion

Claire Syntalion is a governed lifecycle intelligence platform with an operator cockpit, backend-owned runtime truth, controlled live-web readiness, portfolio/acquisition intelligence, breakthrough/design escalation, recursive memory, and safety-first update governance.

## Current Runtime

- Backend entrypoint: `main.py` -> `runtime_core.app:create_app`
- Backend boundary: `runtime_core/` is the active runtime package; `backend/` remains the ASGI adapter boundary
- Intelligence core: `runtime_core/`
- Operator cockpit: `frontend/`
- Primary dashboard: `http://127.0.0.1:8000/dashboard`
- Local dashboard alias: `http://127.0.0.1:8000/dashboard/local`
- Canonical dashboard assets: `frontend/command_center/modern/platform_dashboard.html`, `platform_dashboard.js`, and `platform_dashboard.css`
- Canonical dashboard state: `GET /api/dashboard/state`
- Mounted route count verified on 2026-05-24: `353`

## Local Start

```bat
LAUNCH_PLATFORM.bat
```

The launcher starts the FastAPI backend and opens the permanent local Claire cockpit as the platform dashboard. The installed backend keeps `/dashboard/local` as a compatibility alias. Live web execution, body reads, automatic updates, runtime mutation, and autonomous execution remain blocked unless explicit governed gates are satisfied.

## Search And Internet Modes

The cockpit search bar has two separate lanes:

- `Search` / Enter launches governed research intake. The query becomes a command plan, metadata-only provider results are quarantined, and evidence promotion requires explicit operator confirmation.
- `Open` opens an external search page. `Open in platform` renders a selected result through the local platform browser with page scripts removed and does not promote the page into evidence.

Provider configuration is controlled by `.env` values such as `PLATFORM_SEARCH_PROVIDER=duckduckgo` and `PLATFORM_ALLOW_REAL_SEARCH_PROVIDER=1`. Keyed providers can use `BRAVE_SEARCH_API_KEY`, `BING_SEARCH_API_KEY`, `SERPAPI_API_KEY`, or `TAVILY_API_KEY`. The active lane contract is exposed at `/api/search/lane-config`.

## Consolidation And Endpoint Governance

The current root system is consolidated through backend-owned route contracts instead of dashboard assumptions.

- Active controls: `GET /api/dashboard/active-control-map` exposes 19 operator-visible controls and their mounted endpoints.
- Endpoint reconciliation: `GET /api/system/endpoint-reconciliation` verifies frontend/backend route alignment, compatibility aliases, and unresolved endpoint drift.
- Dependency chain proof: `GET /api/system/dependency-chain-proof` verifies the dashboard-to-runtime-to-provider-to-pipeline-to-output-to-update-governance chain.
- Industry standard endpoint package: `GET /api/system/industry-standard-endpoint-package` and `GET /api/system/endpoint-standard-settings` define the expected endpoint package against OpenAPI, OWASP, NIST, ISO, SLSA, CycloneDX, and OpenTelemetry expectations.
- Lifecycle route contracts are available at `/api/lifecycle/center-route-contract`, `/api/lifecycle/route-contracts`, and `/api/lifecycle/select-route`.
- Update governance install endpoints are present for operator review/stage/apply flows, but automatic update execution remains blocked unless owner gates are satisfied.
- Design/CAD endpoints are review-ready at `/design-portal/contract`, `/design-portal/status`, and `/cad/intent`; CAD export remains intentionally disabled until explicit implementation authority is granted.
- Re-emergence taxonomy endpoints are route-ready at `/api/technology/reemergence-taxonomy` and `/api/technology/reemergence-classify`, with 8 primary categories, 7 signal families, and 12 pattern types from the operator category/timeline notes.
- Causal engine intake is deferred until cleanup and consolidation proof remain clean, so newly prepared causal files can be attached without mixing them into stale roots.

## Verification

```bat
.venv\Scripts\python.exe -B -m pytest tests -q
```

Fast consolidation checks:

```bat
.venv\Scripts\python.exe -B -m pytest tests\test_endpoint_reconciliation_compat.py tests\test_dependency_chain_proof.py tests\test_industry_standard_endpoint_package.py tests\test_legacy_proof_routes_current_canonical.py tests\test_s1323_s1350_dashboard_active_control_map.py -q
```

## Cleanup State

Historical handoff packs and dated cleanup archives have been removed from the product root. The active dashboard configuration is exposed at `/api/platform/dashboard-config`; file readiness remains at `/api/system/file-readiness` and route integrity at `/api/system/route-integrity`.

Historical cleanup candidates and archived dashboards must stay review-only unless explicitly promoted by operator instruction.

## Migration Note

`runtime_core` is the canonical runtime surface. The legacy `claire` package is intentionally preserved only as a tombstone for the current deprecation window; removal is planned after two releases or 30 days. New code should use `runtime_core` imports and `PLATFORM_*` configuration only.
