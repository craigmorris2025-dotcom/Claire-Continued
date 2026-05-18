# Cockpit Backend API Contract Input v19.62

Generated: 2026-05-11T09:19:07.716657Z

Rule: Cockpit JavaScript should consume these backend contracts through one adapter layer, not duplicate backend logic.

## Backend Surfaces for New Cockpit

### boot_health
- Purpose: prove app is alive and runtime can be reached
- Route count: 64
- Owner candidate count: 56
  - `GET /` from `backups/v17_64_1_functional_operator_dashboard_wiring/20260509_183242/claire/app.py`
  - `GET /health` from `backups/v17_64_1_functional_operator_dashboard_wiring/20260509_183242/claire/app.py`
  - `GET /` from `backups/v17_65_runtime_truth_contract_repair/20260509_181910/claire/app.py`
  - `GET /health` from `backups/v17_65_runtime_truth_contract_repair/20260509_181910/claire/app.py`
  - `GET /` from `backups/v17_66_discovery_breakthrough_innovation_route_audit/20260509_184204/claire/app.py`
  - `GET /health` from `backups/v17_66_discovery_breakthrough_innovation_route_audit/20260509_184204/claire/app.py`
  - `GET /` from `backups/v17_67_autodesign_handoff_contract/20260509_184735/claire/app.py`
  - `GET /health` from `backups/v17_67_autodesign_handoff_contract/20260509_184735/claire/app.py`
  - `GET /` from `backups/v17_68_design_portal_output_contract/20260509_184933/claire/app.py`
  - `GET /health` from `backups/v17_68_design_portal_output_contract/20260509_184933/claire/app.py`
  - `GET /` from `backups/v17_69_buildability_validation_stack/20260509_185332/claire/app.py`
  - `GET /health` from `backups/v17_69_buildability_validation_stack/20260509_185332/claire/app.py`
  - `GET /` from `backups/v17_70_internet_readiness_verification/20260509_185527/claire/app.py`
  - `GET /health` from `backups/v17_70_internet_readiness_verification/20260509_185527/claire/app.py`
  - `GET /` from `backups/v17_71_governed_update_pack_staging/20260509_185929/claire/app.py`
  - `GET /health` from `backups/v17_71_governed_update_pack_staging/20260509_185929/claire/app.py`
  - `GET /` from `backups/v17_72_rollback_aware_update_plan_contract/20260509_190143/claire/app.py`
  - `GET /health` from `backups/v17_72_rollback_aware_update_plan_contract/20260509_190143/claire/app.py`
  - `GET /` from `backups/v17_73_automatic_update_runner_gate/20260509_190409/claire/app.py`
  - `GET /health` from `backups/v17_73_automatic_update_runner_gate/20260509_190409/claire/app.py`
  - `GET /` from `backups/v17_74_update_governance_regression_lock/20260509_190627/claire/app.py`
  - `GET /health` from `backups/v17_74_update_governance_regression_lock/20260509_190627/claire/app.py`
  - `GET /` from `backups/v17_75_2_workspace_dashboard_search_command_prep/20260509_192529/claire/app.py`
  - `GET /health` from `backups/v17_75_2_workspace_dashboard_search_command_prep/20260509_192529/claire/app.py`
  - `GET /` from `backups/v17_75_full_end_to_end_proof_pack/20260509_190836/claire/app.py`
  - `GET /health` from `backups/v17_75_full_end_to_end_proof_pack/20260509_190836/claire/app.py`
  - `GET /` from `backups/v17_76_platform_endpoint_smoke_proof/20260509_193317/claire/app.py`
  - `GET /health` from `backups/v17_76_platform_endpoint_smoke_proof/20260509_193317/claire/app.py`
  - `GET /` from `backups/v17_77_platform_launch_hardening/20260509_193754/claire/app.py`
  - `GET /health` from `backups/v17_77_platform_launch_hardening/20260509_193754/claire/app.py`

### dashboard_payload
- Purpose: single current bridge for dashboard/cockpit state
- Route count: 8
- Owner candidate count: 127
  - `GET /dashboard/runtime-truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183718/claire/api/routes_runtime_truth.py`
  - `GET /dashboard/runtime-truth` from `backups/v17_65_runtime_truth_contract_repair/20260509_183932/claire/api/routes_runtime_truth.py`
  - `GET /dashboard/state` from `backups/v17_75_1_dashboard_backend_bridge_repair/20260509_191456/claire/api/routes_operator_dashboard.py`
  - `GET /dashboard/state` from `claire/api/routes_operator_dashboard.py`
  - `GET /dashboard/runtime-truth` from `claire/api/routes_runtime_truth.py`
  - `POST /dashboard` from `claire/api/search_bar_dashboard_api.py`
  - `GET /dashboard` from `claire/internet_operations_dashboard/api_routes.py`
  - `POST /dashboard` from `claire/internet_runtime_integration/api_routes.py`

### runtime_lifecycle
- Purpose: 30-stage runtime, lifecycle state, run execution, pipeline outputs
- Route count: 27
- Owner candidate count: 262
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
  - `GET /runs/{run_id}/files` from `quarantine_legacy_placeholders/backend/routes/backend_export_browser_route.py`
  - `GET /runs/{run_id}/files/{filename}` from `quarantine_legacy_placeholders/backend/routes/backend_export_browser_route.py`

### search_provider
- Purpose: search bar provider path, web search, provider preview
- Route count: 22
- Owner candidate count: 409
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

### governed_web_probe
- Purpose: governed web, trust, allowlist, rate limits, probes, live boundary
- Route count: 25
- Owner candidate count: 297
  - `GET /internet/live-probe/status` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/contract` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `POST /internet/live-probe/run` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/last` from `backups/v17_84_1_live_probe_body_compatibility_repair/20260509_205426/claire/api/routes_governed_live_probe.py`
  - `POST /probe` from `claire/api/real_provider_operator_probe_routes.py`
  - `GET /internet/evidence-promotion` from `claire/api/routes_evidence_promotion_gate.py`
  - `GET /internet/evidence-promotion/summary` from `claire/api/routes_evidence_promotion_gate.py`
  - `POST /internet/evidence-promotion/rebuild` from `claire/api/routes_evidence_promotion_gate.py`
  - `POST /internet/evidence-promotion/promote-approved` from `claire/api/routes_evidence_promotion_gate.py`
  - `GET /internet/evidence-promotion/status` from `claire/api/routes_evidence_promotion_gate.py`
  - `GET /internet/live-probe/status` from `claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/contract` from `claire/api/routes_governed_live_probe.py`
  - `POST /internet/live-probe/run` from `claire/api/routes_governed_live_probe.py`
  - `POST /internet/live-probe/run-confirmed` from `claire/api/routes_governed_live_probe.py`
  - `POST /internet/live-probe/run-adapter` from `claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/adapter/status` from `claire/api/routes_governed_live_probe.py`
  - `GET /internet/live-probe/last` from `claire/api/routes_governed_live_probe.py`
  - `GET /internet/readiness` from `claire/api/routes_internet_readiness.py`
  - `GET /internet/readiness/summary` from `claire/api/routes_internet_readiness.py`
  - `POST /internet/readiness/rebuild` from `claire/api/routes_internet_readiness.py`
  - `GET /internet/operations/status` from `claire/api/routes_internet_readiness.py`
  - `POST /probe` from `claire/governed_web/real_provider_operator_probe_route.py`
  - `POST /internet` from `claire/internet_activation/api_routes.py`
  - `GET /internet/evidence` from `claire/internet_activation/api_routes.py`
  - `GET /internet/evidence/{evidence_id}` from `claire/internet_activation/api_routes.py`

### runtime_truth_evidence
- Purpose: evidence queue, runtime truth, truth firewall/read/search
- Route count: 0
- Owner candidate count: 94

## Do Not Do

- Do not let frontend own source-of-truth logic.
- Do not create multiple fetch owners for the same backend surface.
- Do not scale the old dashboard shell.
- Do not delete legacy backend/frontend files until ownership and parity are proven.
