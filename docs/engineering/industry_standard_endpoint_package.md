# Industry Standard Endpoint Package

Schema: `claire.industry_standard_endpoint_package.v1`
Status: `ready`

## Standards
- OpenAPI 3.1: /openapi.json plus this endpoint expectation package
- OWASP ASVS / OWASP LLM Top 10: operator-gated request bodies, no autonomous body reads, no unsafe tool execution
- NIST AI RMF: governed route gates, review queues, readiness scoring, runtime truth
- ISO/IEC 42001: change-control and update-governance routes remain owner approved
- NIST CSF 2.0: status, proof, rollback, and readiness endpoints
- NIST SSDF / SP 800-218: tests, py_compile, package staging, owner review before install
- SLSA: governed update package file manifest and rollback snapshot requirement
- CycloneDX SBOM: package payload must expose files, checksums, and dependency metadata before apply
- OpenTelemetry: runtime status, proof pack, route integrity, and event outputs

## Critical Endpoints
- GET /api/dashboard/state (dashboard_truth): claire.dashboard.cockpit_dashboard_state
- GET /api/dashboard/active-control-map (active_controls): runtime_core.api.dashboard_active_control_map
- GET /api/search/providers/status (provider_readiness): runtime_core.api.governed_provider_readiness_routes
- POST /internet/live-probe/run (governed_live_probe): runtime_core.api.routes_governed_live_probe
- POST /api/update-governance/open-web/install/stage (update_governance): runtime_core.api.routes_open_web_update_governance
- POST /api/update-governance/open-web/install/apply (update_governance): runtime_core.api.routes_open_web_update_governance
- POST /evaluate (pipeline_evaluate): runtime_core.api.routes_pipeline
- GET /design-portal/status (design_portal): runtime_core.api.routes_design_portal_output
- GET /design-portal/contract (design_portal): runtime_core.api.routes_design_portal_output
- GET /cad/intent (cad_intent): runtime_core.api.routes_design_portal_output
