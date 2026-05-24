# Dependency-to-Dependency End-to-End Proof

Status: `clean_e2e_review_proof`
Generated: `2026-05-24T01:01:43.195113Z`

## Chain
- passed: GET /api/dashboard/state -> claire.dashboard.cockpit_dashboard_state
- passed: GET /api/dashboard/active-control-map -> claire.api.dashboard_active_control_map
- passed: GET /runtime/status -> claire.api.operator_cockpit_runtime
- passed: GET /api/search/providers/status -> claire.api.governed_provider_readiness_routes
- passed: GET /api/search/governed/query/payload -> claire.api.governed_query_compiler_routes
- passed: GET /api/evidence/quarantine/payload -> claire.api.governed_quarantine_evidence_routes
- passed: POST /evaluate -> claire.api.routes_pipeline
- passed: GET /api/portfolio/artifacts/latest -> claire.api.portfolio_artifacts
- passed: GET /design-portal/contract -> claire.api.routes_design_portal_output
- passed: GET /cad/intent -> claire.api.routes_design_portal_output
- passed: GET /api/update-governance/open-web/panel -> claire.api.routes_open_web_update_governance
- passed: GET /api/system/endpoint-reconciliation -> claire.api.routes_endpoint_reconciliation_report
- passed: GET /api/system/industry-standard-endpoint-package -> claire.api.routes_industry_standard_endpoint_package

## Boundaries
- Live provider/network success is not required for this proof.
- CAD export remains blocked; CAD intent is reviewable.
- Automatic update apply remains owner-gated.
