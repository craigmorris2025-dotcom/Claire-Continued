# Current State

Verified date: 2026-05-24

Baseline artifacts:

- Backend pytest baseline: `reports/backend_baseline_20260524_pytest.txt`
- Backend endpoint baseline: `reports/backend_baseline_20260524_ACTIVE_ENDPOINTS.json`
- Final pytest proof: `reports/backend_final_20260524_pytest.txt`
- Final endpoint dump: `reports/backend_final_20260524_ACTIVE_ENDPOINTS.json`
- Frontend fetch map: `reports/frontend_fetch_map_20260524.txt`
- Endpoint reconciliation: `reports/endpoint_reconciliation_20260524.md`

Runtime truth:

- active app: `main.py -> claire.app:create_app`
- route count: `350`
- dashboard: `GET /dashboard`
- dashboard state: `GET /api/dashboard/state`
- active control map: `GET /api/dashboard/active-control-map`
- endpoint reconciliation: `GET /api/system/endpoint-reconciliation`
- dependency proof: `GET /api/system/dependency-chain-proof`

Endpoint reconciliation:

- `active`: 65
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
