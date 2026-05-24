# Contract Governance

Verified date: 2026-05-24

Claire's v1.0 hardening state treats contracts as the governing layer between UI controls, runtime behavior, lifecycle routes, and external standards.

Governed surfaces:

- endpoint reconciliation: `GET /api/system/endpoint-reconciliation`
- dependency proof: `GET /api/system/dependency-chain-proof`
- standards control map: `GET /api/system/standards-control-map`
- dashboard standards alias: `GET /api/dashboard/standards-control-map`
- pipeline activation map: `GET /api/pipelines/activation`
- Design Portal contract: `GET /design-portal/contract`
- CAD intent: `GET /cad/intent`
- CAD export contract: `GET /cad/export-contract`

Governance rules:

- new frontend calls must reconcile against active backend endpoints
- stale aliases are tolerated only when they point to canonical backend owners
- lifecycle route decisions must flow through ACS2 and center-route contracts
- standards controls must map to a route, control, test, gate, and runtime behavior
- Design Portal output can produce CAD intent, but export remains disabled
- live provider execution and runtime mutation remain owner-gated

Machine artifacts:

- `reports/endpoint_reconciliation_20260524_v1.md`
- `reports/v1_0_route_contract_test_gate_map_20260524.json`
- `reports/v1_0_standards_control_map_20260524.json`
- `reports/v1_0_cad_export_contract_20260524.json`
- `reports/v1_0_runtime_behavior_manifest_20260524.json`
