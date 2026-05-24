# Current State

Verified date: 2026-05-24

Baseline artifacts:

- Backend pytest baseline: `reports/backend_baseline_20260524_pytest.txt`
- Backend endpoint baseline: `reports/backend_baseline_20260524_ACTIVE_ENDPOINTS.json`
- Final pytest proof: `reports/backend_final_20260524_pytest.txt`
- Final endpoint dump: `reports/backend_final_20260524_ACTIVE_ENDPOINTS.json`
- Frontend fetch map: `reports/frontend_fetch_map_20260524.txt`
- Endpoint reconciliation: `reports/endpoint_reconciliation_20260524.md`
- v1.0 full pytest: `reports/v1_0_hardening_full_pytest_20260524.txt`
- v1.0 active endpoints: `reports/v1_0_active_endpoints_20260524.json`
- v1.0 runtime behavior: `reports/v1_0_runtime_behavior_manifest_20260524.json`
- v1.0 runtime truth freeze: `reports/v1_0_runtime_truth_freeze_20260524.json`
- v1.0 route/test/gate map: `reports/v1_0_route_contract_test_gate_map_20260524.json`
- v1.0 standards map: `reports/v1_0_standards_control_map_20260524.json`
- v1.0 CAD export contract: `reports/v1_0_cad_export_contract_20260524.json`
- v1.0 dashboard/backend route map: `reports/v1_0_dashboard_backend_route_manifest_20260524.json`

Runtime truth:

- active app: `main.py -> claire.app:create_app`
- route count: `353`
- dashboard: `GET /dashboard`
- dashboard state: `GET /api/dashboard/state`
- active control map: `GET /api/dashboard/active-control-map`
- endpoint reconciliation: `GET /api/system/endpoint-reconciliation`
- dependency proof: `GET /api/system/dependency-chain-proof`

Endpoint reconciliation:

- `active`: 66
- `stale_alias`: 22
- `duplicate`: 7
- `remove`: 93
- `missing`: 0

Design and CAD:

- `GET /design-portal/status`: `contract_ready`
- `GET /design-portal/contract`: mounted
- `GET /design-portal/output`: mounted
- `POST /design-portal/build-from-run`: mounted
- `GET /cad/intent`: `intent_review_ready`
- `GET /cad/export-contract`: `contract_prepared_export_disabled`
- CAD export: disabled

ACS2:

- registry owner: `claire/pipeline/activation_registry.py`
- API: `GET /api/pipelines/activation`
- decision layer: `ACS2 trigger-score-route execution map`
- docs: `docs/architecture/03_pipeline_registry.md`, `docs/architecture/04_trigger_score_route_map.md`

Causal/emergence:

- contract endpoint: `GET /api/emergence/causal-contract`
- assessment endpoint: `POST /api/emergence/causal-assess`
- dependency proof intake status: `contract_ready_runtime_mutation_blocked`

Verification:

- targeted endpoint compatibility tests passed
- design/CAD contract tests passed
- operator-experience tests passed
- ACS2 trigger-score-route tests passed
- full pytest passed with only existing `datetime.utcnow()` deprecation warnings
- v1.0 full-system pytest passed with the same known deprecation warnings
