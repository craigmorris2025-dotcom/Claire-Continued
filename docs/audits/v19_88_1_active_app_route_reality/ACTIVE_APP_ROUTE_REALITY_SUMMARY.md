# Claire v19.88.1 Active App Route Reality

Generated: 2026-05-13T04:04:27.698907+00:00

## Policy
- audit_only: **True**
- mutated_files: **False**
- mounted_routes: **False**
- rewired_dashboard: **False**
- enabled_live_internet: **False**
- runtime_truth_mutated: **False**

- Active app loaded: **True**
- Source: `claire.app:create_app`
- Active mounted route count: **58**

## Missing Required Operational Endpoints
- `/api/feeds/live-source-catalog/status`
- `/api/feeds/live-source-catalog/health`
- `/api/live-intelligence/status`

## Surface Readiness
### boot_core
- Complete: **True**
- Present: /, /health, /docs, /openapi.json
- Missing: none

### dashboard_payload
- Complete: **True**
- Present: /dashboard/payload/status, /dashboard/payload
- Missing: none

### continuous_runtime
- Complete: **True**
- Present: /runtime/continuous/status, /runtime/continuous/start, /runtime/continuous/review-queue
- Missing: none

### governed_search
- Complete: **True**
- Present: /api/dashboard/search/provider/status, /api/dashboard/search/provider/probe, /api/dashboard/search/live, /api/dashboard/search/smoke/google
- Missing: none

### live_source_catalog
- Complete: **False**
- Present: none
- Missing: /api/feeds/live-source-catalog/status, /api/feeds/live-source-catalog/health

### live_intelligence
- Complete: **False**
- Present: none
- Missing: /api/live-intelligence/status

## Next Repair Rule
Repair only missing required operational endpoints in the active create_app route stack. Do not restore archived routes blindly.
