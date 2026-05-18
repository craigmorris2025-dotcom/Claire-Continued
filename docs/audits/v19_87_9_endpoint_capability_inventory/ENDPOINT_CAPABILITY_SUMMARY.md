# Claire v19.87.9 Endpoint Capability Inventory

Generated: 2026-05-13T02:47:41.727455+00:00

## Policy
- audit_only: **True**
- mutated_files: **False**
- rewired_dashboard: **False**
- enabled_live_internet: **False**
- restored_quarantine: **False**
- runtime_truth_mutated: **False**

## Counts
- static_route_hits: **948**
- unique_static_route_paths: **210**
- endpoint_references: **24079**
- unique_referenced_paths: **208**
- live_openapi_paths: **0**
- referenced_paths_missing_from_live_openapi: **206**
- source_catalog_live_web_surface_refs: **229329**

## Key endpoint probes
- `/` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/health` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/docs` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/openapi.json` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/dashboard/payload/status` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/dashboard/payload` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/api/dashboard/search/provider/status` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/api/dashboard/search/provider/probe` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/api/dashboard/search/live` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>
- `/api/dashboard/search/smoke/google` → unreachable / None / URLError: <urlopen error [WinError 10061] No connection could be made because the target machine actively refused it>

## System areas
### backend_api_routes
- routes: 131
- endpoint_refs: 591
- source_catalog_refs: 298

### dashboard_cockpit_frontend
- routes: 675
- endpoint_refs: 11680
- source_catalog_refs: 16366

### evidence_review_governance
- routes: 1
- endpoint_refs: 177
- source_catalog_refs: 1931

### launcher_startup
- routes: 0
- endpoint_refs: 16
- source_catalog_refs: 4

### live_web_source_provider
- routes: 82
- endpoint_refs: 1460
- source_catalog_refs: 9817

### runtime_orchestration
- routes: 50
- endpoint_refs: 5938
- source_catalog_refs: 8205

### tests_contracts
- routes: 0
- endpoint_refs: 21
- source_catalog_refs: 63

### uncategorized
- routes: 9
- endpoint_refs: 4196
- source_catalog_refs: 192645

## Missing live OpenAPI paths referenced by code/frontend
- `/api/`
- `/api/command`
- `/api/command\`
- `/api/commands`
- `/api/core-run-output/latest`
- `/api/dashboard/layout`
- `/api/dashboard/payload`
- `/api/dashboard/payload/status`
- `/api/dashboard/search`
- `/api/dashboard/search/live`
- `/api/dashboard/search/live\`
- `/api/dashboard/search/provider`
- `/api/dashboard/search/provider/`
- `/api/dashboard/search/provider/probe`
- `/api/dashboard/search/provider/status`
- `/api/dashboard/search/provider/status\`
- `/api/dashboard/search/provider\`
- `/api/dashboard/search/smoke/`
- `/api/dashboard/search/smoke/google`
- `/api/dashboard/search/smoke/google\`
- `/api/dashboard/search\`
- `/api/dashboard/state`
- `/api/dashboard/state\`
- `/api/dashboard/system-status`
- `/api/desktop-app/status`
- `/api/enhanced-interface/action`
- `/api/enhanced-interface/status`
- `/api/evaluate`
- `/api/evaluate/async`
- `/api/events`
- `/api/events/`
- `/api/exports/acquisition-preview`
- `/api/feeds/activation-check`
- `/api/feeds/activation-status`
- `/api/feeds/audit`
- `/api/feeds/governed-activation/prepare`
- `/api/feeds/governed-activation/status`
- `/api/feeds/index-universes`
- `/api/feeds/live-orchestration/run`
- `/api/feeds/live-orchestration/status`
- `/api/feeds/live-source-catalog/health`
- `/api/feeds/live-source-catalog/health-check`
- `/api/feeds/live-source-catalog/packs`
- `/api/feeds/live-source-catalog/resolve`
- `/api/feeds/live-source-catalog/status`
- `/api/feeds/offline-universe/resolve`
- `/api/feeds/offline-universe/status`
- `/api/feeds/public-company-live/scan`
- `/api/feeds/public-company-live/status`
- `/api/feeds/public-company-sources`
- `/api/feeds/scan`
- `/api/feeds/status`
- `/api/governance/audit`
- `/api/governance/evaluate`
- `/api/health`
- `/api/internet/campaigns`
- `/api/internet/source-trust`
- `/api/launch/regression-lock`
- `/api/lifecycle/stage-registry`
- `/api/lifecycle/threshold-provenance`
- `/api/live-intelligence/activate-candidates`
- `/api/live-intelligence/cluster`
- `/api/live-intelligence/connectors/run`
- `/api/live-intelligence/connectors/status`
- `/api/live-intelligence/detect-gaps`
- `/api/live-intelligence/entities`
- `/api/live-intelligence/extract`
- `/api/live-intelligence/history`
- `/api/live-intelligence/latest`
- `/api/live-intelligence/monitor/run`
- `/api/live-intelligence/monitor/status`
- `/api/live-intelligence/scan-plan`
- `/api/live-intelligence/status`
- `/api/live-intelligence/synthesize`
- `/api/market-universe`
- `/api/modes/evaluate`
- `/api/modes/recent`
- `/api/modes/status`
- `/api/opportunities/enrich-preview`
- `/api/opportunities/enrichment-status`
- `/api/opportunities/fusion-preview`
- `/api/opportunities/fusion-status`
- `/api/opportunities/generate`
- `/api/opportunities/run-candidate`
- `/api/opportunities/search-needed-solutions`
- `/api/platform/current`
- `/api/platform/current\`
- `/api/platform/resolve`
- `/api/platform/resolve/{component}`
- `/api/platform/resolve/{component}\`
- `/api/platform/resolve\`
- `/api/platform/status`
- `/api/platform/status\`
- `/api/platform/target`
- `/api/platform/target\`
- `/api/portable/status`
- `/api/proxy/ping`
- `/api/rescan`
- `/api/research/evidence`
- `/api/research/evidence/add`

## Live operation chain
- launcher/startup
- FastAPI app
- backend route mounts
- canonical payload endpoints
- cockpit/frontend fetches
- source catalog
- allowlist/trust/rate-limit policy
- provider adapter
- controlled probe
- source result schema
- evidence basket
- review gate
- runtime route decision
- cockpit output rendering

