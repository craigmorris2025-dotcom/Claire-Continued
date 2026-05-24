# Dependency-to-Dependency End-to-End Proof

Status: `clean_e2e_review_proof`
Generated: `2026-05-24T22:35:21.800501Z`

## Chain
- passed: GET /api/dashboard/state -> runtime_core.dashboard.cockpit_dashboard_state
- passed: GET /api/dashboard/active-control-map -> runtime_core.api.dashboard_active_control_map
- passed: GET /runtime/status -> runtime_core.api.operator_cockpit_runtime
- passed: GET /api/search/providers/status -> runtime_core.api.governed_provider_readiness_routes
- passed: GET /api/search/governed/query/payload -> runtime_core.api.governed_query_compiler_routes
- passed: GET /api/evidence/quarantine/payload -> runtime_core.api.governed_quarantine_evidence_routes
- passed: POST /evaluate -> runtime_core.api.routes_pipeline
- passed: GET /api/portfolio/artifacts/latest -> runtime_core.api.portfolio_artifacts
- passed: GET /design-portal/contract -> runtime_core.api.routes_design_portal_output
- passed: GET /cad/intent -> runtime_core.api.routes_design_portal_output
- passed: GET /api/update-governance/open-web/panel -> runtime_core.api.routes_open_web_update_governance
- passed: GET /api/system/endpoint-reconciliation -> runtime_core.api.routes_endpoint_reconciliation_report
- passed: GET /api/system/industry-standard-endpoint-package -> runtime_core.api.routes_industry_standard_endpoint_package

## Boundaries
- Live provider/network success is not required for this proof.
- CAD export remains blocked; CAD intent is reviewable.
- Automatic update apply remains owner-gated.
