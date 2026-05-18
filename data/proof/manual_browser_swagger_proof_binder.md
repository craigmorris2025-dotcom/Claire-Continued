# Claire v17.79 Manual Browser + Swagger Proof Binder

Generated: 2026-05-13T11:19:00.838871Z

Status: **READY_FOR_MANUAL_BROWSER_SWAGGER_PROOF**

Recommendation: Open the URLs, complete the dashboard walkthrough, and run Swagger Try it out tests. Automatic web/update/agent execution remains disabled.

## Start

```bat
START_CLAIRE_SAFE.bat
```

## Browser URLs

- [swagger_docs] http://127.0.0.1:8000/docs
  - Expected: Swagger UI opens and shows Claire API routes.
- [operator_dashboard_state] http://127.0.0.1:8000/operator/dashboard/state
  - Expected: JSON response includes contract_version, mission, route_gate, surfaces, proof, updates.
- [search_capabilities] http://127.0.0.1:8000/operator/search/capabilities
  - Expected: JSON response shows permanent search bar, normal web search prepared, runtime search enabled, agent command prepared.
- [runtime_truth] http://127.0.0.1:8000/runtime/truth
  - Expected: Runtime truth endpoint responds with canonical truth data or visible missing state.
- [route_audit] http://127.0.0.1:8000/routes/audit
  - Expected: Route audit confirms discovery/breakthrough/innovation and AutoDesign/Design Portal route rules.
- [autodesign_handoff] http://127.0.0.1:8000/autodesign/handoff
  - Expected: AutoDesign handoff contract responds and does not fake missing design data.
- [design_portal_output] http://127.0.0.1:8000/design-portal/output
  - Expected: Design Portal output contract responds with design sections or visible missing state.
- [internet_readiness] http://127.0.0.1:8000/internet/readiness
  - Expected: Internet readiness responds; live uncontrolled web remains disabled.
- [update_regression_lock] http://127.0.0.1:8000/updates/regression-lock
  - Expected: Update governance lock responds; automatic/background execution remains disabled.
- [platform_smoke] http://127.0.0.1:8000/proof/platform-smoke
  - Expected: Platform smoke proof responds with domain status and Stop/Go.
- [desktop_startup] http://127.0.0.1:8000/desktop/startup
  - Expected: Desktop startup reliability report responds.

## Swagger Try it out tests

Open: http://127.0.0.1:8000/docs

### search_runtime_query

- Method/path: `POST /operator/search/query`
- Body:

```json
{
  "query": "runtime truth",
  "mode": "runtime",
  "limit": 5
}
```
- Expected: Returns completed runtime/system search response with result list shape.

### command_parse_autodesign

- Method/path: `POST /operator/command/parse`
- Body:

```json
{
  "query": "open autodesign"
}
```
- Expected: Returns command parse result; execution_enabled remains false.

### proof_platform_rebuild

- Method/path: `POST /proof/platform-smoke/rebuild`
- Body:

```json
{}
```
- Expected: Rebuilds platform smoke proof and returns domain status.

### desktop_startup_rebuild

- Method/path: `POST /desktop/startup/rebuild`
- Body:

```json
{}
```
- Expected: Rebuilds desktop startup report and returns Stop/Go status.

## Dashboard walkthrough

- [ ] Run START_CLAIRE_SAFE.bat.
- [ ] Confirm Swagger opens at http://127.0.0.1:8000/docs.
- [ ] Confirm the dashboard opens from frontend/command_center/modern/index.html.
- [ ] Wait for backend startup, then press dashboard Refresh/Search if Backend Offline appears.
- [ ] Confirm dashboard top status says Backend Online.
- [ ] Confirm the permanent search bar remains visible.
- [ ] Switch through workspaces: Mission, Routes, Discovery, AutoDesign, Design Portal, Portfolio, Acquisition, Internet, Updates, Proof, Diagnostics.
- [ ] Run Runtime search in the command/search bar with query: runtime truth.
- [ ] Run Command mode with query: open autodesign.
- [ ] Run Web mode with query: test web search gate. Confirm it returns prepared_not_executed, not fake web results.

## Evidence template

`data/proof/manual_browser_swagger_evidence_template.json`

Do not mark final launch ready until required evidence slots are checked.

## Warnings

- manual_evidence_not_yet_completed:25_required_slots
- prior_report_stop:v17_76_platform_smoke
- prior_report_stop:v17_77_launch_hardening
- prior_report_stop:v17_78_desktop_startup
