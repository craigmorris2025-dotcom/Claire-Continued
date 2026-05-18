# Claire Syntalion v19.61
## Active System Working Pathway Map

Generated: 2026-05-11T09:15:19.964722Z

## Current Working State

- **backend_status**: past recovery; active app boot and route/payload surface expected
- **dashboard_status**: legacy/transitional; should not be scaled further
- **next_architecture_status**: enterprise cockpit should consume active backend payloads/routes instead of inheriting old dashboard ownership
- **safety_rule**: No deletion or dashboard replacement in this pack. Map first, build second.

## Inferred Active Pathway

### 1. Launcher / command entry
- Cockpit implication: New cockpit must not replace launch mechanics until boot path is proven.

### 2. FastAPI app factory
- Cockpit implication: Cockpit should be served or linked by active FastAPI only after stable route ownership is proven.

### 3. Runtime / lifecycle / pipeline APIs
- Cockpit implication: Runtime panels should consume backend route outputs only.
- Current route count: 27
  - `GET /runtime/truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `GET /runtime/state` from `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `POST /runtime/truth/rebuild` from `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `GET /runtime/truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `GET /runtime/state` from `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `POST /runtime/truth/rebuild` from `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `POST /run` from `claire/api/endpoints.py`
  - `GET /updates/runner-gate` from `claire/api/routes_automatic_update_runner_gate.py`
  - `GET /updates/runner-gate/summary` from `claire/api/routes_automatic_update_runner_gate.py`
  - `POST /updates/runner-gate/rebuild` from `claire/api/routes_automatic_update_runner_gate.py`
  - `GET /deals/pipeline` from `claire/api/routes_dashboard.py`
  - `POST /first-use/run` from `claire/api/routes_dashboard_e2e.py`
  - `GET /history/{run_id}` from `claire/api/routes_history.py`
  - `POST /pipeline/evaluate` from `claire/api/routes_pipeline.py`
  - `POST /evaluate` from `claire/api/routes_pipeline.py`
  - `GET /history/{run_id}` from `claire/api/routes_proxy.py`
  - `GET /runtime/truth` from `claire/api/routes_runtime_truth.py`
  - `GET /runtime/state` from `claire/api/routes_runtime_truth.py`
  - `POST /runtime/truth/rebuild` from `claire/api/routes_runtime_truth.py`
  - `POST /run-due` from `claire/governed_campaign_scheduler/api_routes.py`
  - `POST /run-due` from `claire/internet_operations_dashboard/api_routes.py`
  - `POST /scheduler/run-due` from `claire/internet_runtime_stability/api_routes.py`
  - `GET /runs` from `quarantine_legacy_placeholders/backend/routes/backend_export_browser_route.py`
  - `POST /runs/rescan` from `quarantine_legacy_placeholders/backend/routes/backend_export_browser_route.py`
  - `GET /runs/{run_id}` from `quarantine_legacy_placeholders/backend/routes/backend_export_browser_route.py`
- Current file count: 1146
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/claire/dashboard_live_search_binding.py`
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/tests/test_v18_85_to_v18_89_dashboard_runtime_governed_search_pack.py`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/claire/dashboard_currency_runtime_order_lock.py`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/data/dashboard_currency_reports/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_manifest.json`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/data/dashboard_currency_reports/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_report.json`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/tests/test_v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack.py`
  - `artifacts/v19_37_to_v19_41_governed_runtime_expansion_manifest.json`
  - `audits/v17_63_active_state_proof_20260509_132540/runtime_truth_contract_scan.json`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/lifecycle_stage_registry.json`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/runtime_surface_registry.json`
  - `backups/claire_v17_58_1_20260507_225951/docs/update_packs/v17.58.1_system_runtime_update_pack.md`
  - `backups/claire_v17_59_20260507_230959/src/claire/runtime_truth/__init__.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_181910/claire/app.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/runtime_truth/runtime_truth_contract_repair.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/data/build_manifests/v17_65_runtime_truth_contract_repair_manifest.json`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/data/runtime/v17_65_runtime_truth_validation.json`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/docs/runtime_truth/v17.65_runtime_truth_contract_repair.md`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183718/tests/test_v17_65_runtime_truth_contract_repair.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/runtime_truth/runtime_truth_contract_repair.py`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/data/build_manifests/v17_65_runtime_truth_contract_repair_manifest.json`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/data/runtime/v17_65_runtime_truth_validation.json`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/docs/runtime_truth/v17.65_runtime_truth_contract_repair.md`
  - `backups/v17_65_runtime_truth_contract_repair/20260509_183932/tests/test_v17_65_runtime_truth_contract_repair.py`

### 4. Dashboard payload API
- Cockpit implication: /dashboard/payload remains the canonical bridge unless the audit proves a better single contract.
- Current route count: 8
  - `GET /dashboard/runtime-truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `GET /dashboard/runtime-truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `GET /dashboard/state` from `backups/v17_75_1_dashboard_backend_bridge_repair/20260509_191456/claire/api/routes_operator_dashboard.py`
  - `GET /dashboard/state` from `claire/api/routes_operator_dashboard.py`
  - `GET /dashboard/runtime-truth` from `claire/api/routes_runtime_truth.py`
  - `POST /dashboard` from `claire/api/search_bar_dashboard_api.py`
  - `GET /dashboard` from `claire/internet_operations_dashboard/api_routes.py`
  - `POST /dashboard` from `claire/internet_runtime_integration/api_routes.py`
- Current file count: 281
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/claire/dashboard_live_search_binding.py`
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/tests/test_v18_85_to_v18_89_dashboard_runtime_governed_search_pack.py`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/claire/dashboard_currency_runtime_order_lock.py`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/data/dashboard_currency_reports/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_manifest.json`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/data/dashboard_currency_reports/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_report.json`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/tests/test_v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack.py`
  - `_claire_archives/v19_00_to_v19_04_actual_run_output_dashboard_binding_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_20_to_v19_24_dashboard_sophistication_no_restructure_pack/frontend/command_center/modern/index.html`
  - `audits/_claire_audit_v19_canonical_dashboard_payload_bridge/canonical_dashboard_payload_bridge_install_report.json`
  - `audits/_claire_audit_v19_dashboard_fetch_wiring_pack/dashboard_fetch_wiring_report.json`
  - `audits/_claire_audit_v19_dashboard_payload_contract/dashboard_payload_contract_audit.json`
  - `audits/_claire_audit_v19_dashboard_payload_coverage/dashboard_payload_coverage_audit.json`
  - `audits/v17_63_active_state_proof_20260509_132540/dashboard_conflict_map.json`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/dashboard_architecture_map.json`
  - `backups/claire_v17_58_1_20260507_225951/data/build_manifests/v17.58.1_dashboard_text_repair_manifest.json`
  - `backups/claire_v17_62_1_20260508_043941/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/claire_v17_62_2_20260508_044716/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/v17_52_modern_operator_dashboard/src/frontend/command_center/modern/index.html`
  - `backups/v17_53_product_dashboard_experience_layer/src/frontend/command_center/modern/index.html`
  - `backups/v17_54_persistent_workspace_operational_flow/src/frontend/command_center/modern/product_dashboard.js`
  - `backups/v17_55_live_intelligence_feed_narrative_flow/src/frontend/command_center/modern/product_dashboard.css`
  - `backups/v17_55_live_intelligence_feed_narrative_flow/src/frontend/command_center/modern/product_dashboard.js`
  - `backups/v17_64_1_functional_operator_dashboard_wiring/20260509_183242/claire/app.py`

### 5. Search/provider/governed web APIs
- Cockpit implication: Search panel must be permanent command/search/research surface, not a simple textbox.
- Current route count: 47
  - `GET /operator/search/capabilities` from `claire/api/operator_dashboard_compat_routes.py`
  - `GET /operator/search/smoke/google` from `claire/api/operator_dashboard_compat_routes.py`
  - `GET /operator/search` from `claire/api/operator_dashboard_compat_routes.py`
  - `POST /operator/search` from `claire/api/operator_dashboard_compat_routes.py`
  - `GET /operator/search/live` from `claire/api/operator_dashboard_compat_routes.py`
  - `POST /operator/search/live` from `claire/api/operator_dashboard_compat_routes.py`
  - `POST /operator/search/query` from `claire/api/operator_dashboard_compat_routes.py`
  - `POST /operator/search/run` from `claire/api/operator_dashboard_compat_routes.py`
  - `GET /innovation/search` from `claire/api/routes_dashboard.py`
  - `GET /patents/search` from `claire/api/routes_dashboard.py`
  - `POST /operator/search/web/run-governed-probe` from `claire/api/routes_governed_live_probe.py`
  - `GET /internet/provider-gate` from `claire/api/routes_internet_provider_gate.py`
  - `GET /internet/provider-gate/summary` from `claire/api/routes_internet_provider_gate.py`
  - `POST /internet/provider-gate/rebuild` from `claire/api/routes_internet_provider_gate.py`
  - `GET /internet/search/provider/status` from `claire/api/routes_internet_provider_gate.py`
  - `GET /search/dashboard-smoke` from `claire/api/routes_live_search_dashboard_smoke.py`
  - `GET /operator/search/capabilities` from `claire/api/routes_operator_search_command.py`
  - `POST /operator/search/query` from `claire/api/routes_operator_search_command.py`
  - `GET /operator/search/web/status` from `claire/api/routes_operator_search_command.py`
  - `POST /operator/search/web` from `claire/api/routes_operator_search_command.py`
  - `GET /operator/search/layer` from `claire/api/routes_operator_search_command.py`
  - `GET /search/visible-result-verification` from `claire/api/routes_visible_query_result_verification.py`
  - `GET /internet/live-probe/status` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/contract` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `POST /internet/live-probe/run` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
- Current file count: 1103
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/claire/dashboard_live_search_binding.py`
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/tests/test_v18_85_to_v18_89_dashboard_runtime_governed_search_pack.py`
  - `backups/claire_v17_62_1_20260508_043941/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/claire_v17_62_2_20260508_044716/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/v17_75_2_workspace_dashboard_search_command_prep/20260509_192529/claire/app.py`
  - `backups/v17_75_2_workspace_dashboard_search_command_prep/20260509_192529/frontend/command_center/modern/index.html`
  - `backups/v17_83_internet_provider_configuration_gate/20260509_203928/claire/app.py`
  - `backups/v17_84_governed_single_query_live_search_probe/20260509_204207/claire/app.py`
  - `backups/v18_72_2_active_launcher_web_route_module_wrapper_repair/20260510_082851/__Users__craig__OneDrive__Desktop__Claire__claire__api__governed_dashboard_live_search_routes.py`
  - `backups/v18_72_2_active_launcher_web_route_module_wrapper_repair/20260510_082851/__Users__craig__OneDrive__Desktop__Claire__claire__api__real_provider_operator_probe_routes.py`
  - `backups/v18_73_2_dashboard_search_provider_probe_separation_repair/20260510_090938/__Users__craig__OneDrive__Desktop__Claire__frontend__command_center__modern__index.html`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/citation_lineage_engine.py`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/claim_verifier.py`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/evidence_conflict_resolver.py`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/governed_live_research.py`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/research_packet_builder.py`
  - `backups/v19_structural_repair_pack_1_1_backend_syntax/20260510_150647/claire/research/live/source_verification_engine.py`
  - `claire/api/governed_dashboard_live_search_routes.py`
  - `claire/api/real_provider_operator_probe_routes.py`
  - `claire/api/routes_internet_provider_gate.py`
  - `claire/api/routes_live_search_dashboard_smoke.py`
  - `claire/api/routes_operator_search_command.py`
  - `claire/api/routes_v19_25_search_execution.py`
  - `claire/api/search_bar_dashboard_api.py`

### 6. Legacy dashboard/frontend fetch layer
- Cockpit implication: Use as reference only. Do not inherit duplicate fetch ownership into new cockpit.
- Current file count: 164
  - `_claire_archives/v18_85_to_v18_89_dashboard_runtime_governed_search_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v18_90_to_v18_94_dashboard_currency_runtime_output_order_lock_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v18_95_to_v18_99_primary_pipeline_connection_desired_output_contract_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_00_to_v19_04_actual_run_output_dashboard_binding_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_05_to_v19_09_route_aware_autonomous_execution_proof_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_10_to_v19_14_live_web_evidence_pipeline_ingestion_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_15_to_v19_19_pipeline_result_quality_blocked_state_pack/frontend/command_center/modern/index.html`
  - `_claire_archives/v19_20_to_v19_24_dashboard_sophistication_no_restructure_pack/frontend/command_center/modern/index.html`
  - `backups/claire_v17_56_20260507_185658/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/claire_operating_environment.css`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/claire_operating_environment.js`
  - `backups/claire_v17_57_58_20260507_224200/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_58_1_20260507_225205/src/frontend/command_center/modern/claire_operating_environment.css`
  - `backups/claire_v17_58_1_20260507_225951/src/frontend/command_center/modern/claire_operating_environment.css`
  - `backups/claire_v17_59_20260507_230959/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_60_20260508_041331/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_61_20260508_041627/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_1_20260508_043941/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/claire_v17_62_1_20260508_043941/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_20260508_042340/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_2_20260508_044716/src/frontend/command_center/modern/claire_dashboard_search.js`
  - `backups/claire_v17_62_2_20260508_044716/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_3_20260508_045136/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_4_20260508_045358/src/frontend/command_center/modern/index.html`
  - `backups/claire_v17_62_5_20260508_050256/src/frontend/command_center/modern/index.html`
- Current frontend fetch count: 14
  - `${BASE_URL}${path}` from `frontend/js/api.js`
  - `${BASE_URL}${path}` from `frontend/js/api.js`
  - `/api/command` from `frontend/js/api.js`
  - `/api/platform/status` from `frontend/js/platform.js`
  - `/api/platform/resolve` from `frontend/js/platform.js`
  - `${API_BASE}/api/update/status` from `frontend/js/updater.js`
  - `${API_BASE}/api/update/apply` from `frontend/js/updater.js`
  - `${API_BASE}/api/update/cache` from `frontend/js/updater.js`
  - `${API_BASE}/api/update/cache` from `frontend/js/updater.js`
  - `${API_BASE}/api/proxy/get?${query}` from `frontend/js/web_connector.js`
  - `${API_BASE}/api/proxy/post` from `frontend/js/web_connector.js`
  - `${API_BASE}/api/proxy/ping` from `frontend/js/web_connector.js`
  - `${API_BASE}/api/connectors/${connectorName}/fetch` from `frontend/js/web_connector.js`
  - `${API_BASE}/api/connectors/status` from `frontend/js/web_connector.js`

## Route Group Counts

| Group | Count |
|---|---:|
| `dashboard_payload_or_dashboard_api` | 8 |
| `governed_web_or_probe_api` | 25 |
| `health_boot_api` | 64 |
| `other_api` | 150 |
| `runtime_pipeline_api` | 27 |
| `search_provider_api` | 22 |

## Cockpit Input Map

- New cockpit root: `frontend/cockpit/`
- Canonical rule: The new cockpit consumes backend runtime APIs and canonical payload contracts. It does not own intelligence logic.
- Legacy dashboard rule: Existing dashboard files are legacy/reference until parity is proven.

## Minimum No-Redesign-Later Requirements

- Permanent top command/search surface included from the start.
- Panel registry included from the start.
- Payload adapter included from the start.
- Runtime/lifecycle panel model included from the start.
- Governed web/search panel included from the start.
- Discovery/trend/portfolio/design/package areas reserved from the start.
- Legacy dashboard remains reference until parity is proven.
