# Standards Control Map

Verified date: 2026-05-24

This layer is additive to `v0.9-endpoint-proof-lock`. It attaches enterprise standards to the locked runtime without changing the proof-lock baseline.

Active routes:

- `GET /api/system/standards-control-map`
- `GET /dashboard/system/standards-control-map`
- `GET /api/system/industry-standard-endpoint-package`

Machine manifest:

- `reports/v1_0_standards_control_map_20260524.json`

| framework | route | control | test | governance gate | runtime behavior |
|---|---|---|---|---|---|
| NIST AI RMF | `/api/emergence/causal-assess` | governed causal and emergence assessment | `tests/test_causal_emergence_contract_intake.py` | manual promotion required; runtime truth mutation blocked | route-vector assessment without route-truth mutation |
| ISO/IEC 42001 | `/api/update-governance/open-web/panel` | AI management-system change review | `tests/test_open_web_update_governance.py` | owner approval before stage/apply | proposals remain review-only until install criteria pass |
| OWASP LLM Top 10 | `/api/cockpit/command/plan` | operator command planning boundaries | `tests/test_endpoint_reconciliation_compat.py` | aliases compute no new truth and unlock no tools | commands produce governed plans without autonomous execution |
| NIST CSF 2.0 | `/api/system/dependency-chain-proof` | govern/identify/protect/detect/respond/recover proof chain | `tests/test_dependency_chain_proof.py` | proof must remain clean before new layers attach | passed/blocked dependency and recovery boundaries are exposed |
| NIST SSDF | `/api/system/endpoint-reconciliation` | secure endpoint change reconciliation | `tests/test_endpoint_reconciliation_compat.py` | no missing frontend-to-backend paths | stale routes disclose compatibility-only behavior |
| SLSA | `/api/update-governance/open-web/install/stage` | staged package provenance and rollback gate | `tests/test_open_web_update_governance.py` | owner-approved proposal and package metadata required | stage prepares evidence without automatic apply |
| CycloneDX | `/api/system/industry-standard-endpoint-package` | SBOM-ready endpoint/package inventory | `tests/test_industry_standard_endpoint_package.py` | package must disclose endpoint owners and dependency expectations | machine-readable inventory for downstream SBOM generation |
| OpenTelemetry | `/runtime/status` | runtime status and observability surface | `tests/test_runtime_truth_canonical_routes.py` | observation cannot mutate runtime truth | runtime, truth, queue, and proof signals are available for trace/metric/log binding |

Authority remains blocked for:

- automatic update apply
- runtime truth mutation
- CAD export
- autonomous live web execution
