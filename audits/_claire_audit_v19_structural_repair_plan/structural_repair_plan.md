# Claire Structural Syntax + Dashboard Wiring Repair Plan

- Generated: `2026-05-10T19:57:48.380898Z`
- Stop/Go: **STOP_BACKEND_SYNTAX_REPAIR_REQUIRED**
- Syntax failures: **68**
- Dashboard fetch count: **0**

## Failure Groups
- `active_backend_startup_blocker`: **1**
- `generated_placeholder_or_incomplete_module`: **34**
- `quarantined_legacy_placeholder`: **29**
- `unknown`: **4**

## Critical claire/app.py Context
   336: # v18.72.2 active launcher create_app web activation wrapper end
   337: 
   338: # v18.73.1 operator dashboard compatibility endpoint wrapper
   339: try:
   340:     _claire_original_create_app_before_v18_73_1 = create_app
   341: 
   342:     def create_app() -> FastAPI:
   343:         app = _claire_original_create_app_before_v18_73_1()
   344:         try:
   345:             from claire.api.operator_dashboard_compat_routes import router as _v18_73_1_operator_compat_router
   346:             app.include_router(_v18_73_1_operator_compat_router)
>> 347: app.include_router(v19_25_search_execution_router)
   348:         except Exception:
   349:             pass
   350:         return app
   351: 
   352:     try:
   353:         app = create_app()
   354:     except Exception:
   355:         pass
   356: except Exception:
   357:     pass
   358: # v18.73.1 operator dashboard compatibility endpoint wrapper end

## Highest Priority Syntax Failures
- **critical** `claire/app.py` line 347: expected 'except' or 'finally' block | app.include_router(v19_25_search_execution_router) | category `active_backend_startup_blocker`
- **high** `claire/autonomous/governance/autonomous_action_policy.py` line 50: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/autonomous/governance/escalation_boundary.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/autonomous/governance/human_review_gate.py` line 42: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/autonomous/governance/self_change_permission_model.py` line 43: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/proof/build_sequence_validator.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/proof/deployment_model_validator.py` line 41: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/proof/implementation_cost_model.py` line 46: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/renderers/architecture_graph_formatter.py` line 46: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/renderers/blueprint_summary_formatter.py` line 33: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/renderers/dependency_graph_formatter.py` line 41: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/design/renderers/design_export_formatter.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/recursive/longitudinal/learning_signal_extractor.py` line 58: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/recursive/longitudinal/run_pattern_miner.py` line 43: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/recursive/longitudinal/strategy_memory_synthesizer.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/recursive/longitudinal/thesis_evolution_tracker.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/citation_lineage_engine.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/claim_verifier.py` line 33: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/evidence_conflict_resolver.py` line 61: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/governed_live_research.py` line 35: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/research_packet_builder.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/research/live/source_verification_engine.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/compatibility_engine.py` line 33: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/component_matcher.py` line 38: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/enterprise_stack_recommender.py` line 37: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/integration_complexity.py` line 42: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/model_governance_assessor.py` line 49: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/technology/technology_catalog.py` line 45: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/benchmark_dataset_loader.py` line 52: unmatched ']' | def Dataset]: | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/benchmark_reporter.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/false_negative_analyzer.py` line 41: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/false_positive_analyzer.py` line 42: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/outcome_label_manager.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/regime_backtester.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **high** `claire/validation/benchmarks/signal_backtester.py` line 34: invalid syntax | raise NotImplementedError | category `generated_placeholder_or_incomplete_module`
- **low** `quarantine_legacy_placeholders/benchmarks/benchmark_dataset_loader.py` line 52: unmatched ']' | def Dataset]: | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/benchmark_reporter.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/false_negative_analyzer.py` line 41: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/false_positive_analyzer.py` line 42: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/outcome_label_manager.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/regime_backtester.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/benchmarks/signal_backtester.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/final_remaining/architecture_graph_formatter.py` line 46: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/final_remaining/blueprint_summary_formatter.py` line 33: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/final_remaining/dependency_graph_formatter.py` line 41: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/final_remaining/design_export_formatter.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/final_remaining/uptime_monitor.py` line 34: expected '(' | def mean time to recovery(self, *args, **kwargs): | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/governance/autonomous_action_policy.py` line 50: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/governance/escalation_boundary.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/governance/human_review_gate.py` line 42: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/governance/self_change_permission_model.py` line 43: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/citation_lineage_engine.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/claim_verifier.py` line 33: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/evidence_conflict_resolver.py` line 61: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/governed_live_research.py` line 35: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/research_packet_builder.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/live/source_verification_engine.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/longitudinal/learning_signal_extractor.py` line 58: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/longitudinal/run_pattern_miner.py` line 43: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/longitudinal/strategy_memory_synthesizer.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/longitudinal/thesis_evolution_tracker.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/proof/build_sequence_validator.py` line 34: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/proof/deployment_model_validator.py` line 41: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **low** `quarantine_legacy_placeholders/proof/implementation_cost_model.py` line 46: invalid syntax | raise NotImplementedError | category `quarantined_legacy_placeholder`
- **medium** `tests/regression/test_runtime_cleanroom.py` line 1: invalid non-printable character U+FEFF | ﻿from pathlib import Path | category `unknown`
- **medium** `tests/regression/test_runtime_smoke.py` line 1: invalid non-printable character U+FEFF | ﻿from tools.active_runtime_check import main as runtime_check_main | category `unknown`
- **medium** `tools/master_control_layer_builder.py` line 1: invalid non-printable character U+FEFF | ﻿#!/usr/bin/env python3 | category `unknown`
- **medium** `tools/pytest_consistency_audit.py` line 71: unterminated string literal (detected at line 71) | print(f" | category `unknown`

## Dashboard Fetch Scan
- No fetch calls detected in `frontend/command_center/modern`. The current dashboard is not contract-wired to backend routes.

## Repair Order
- 1. Repair claire/app.py syntax first; backend cannot start until this is fixed.
- 2. Separate active-runtime modules from placeholder/quarantined modules.
- 3. Repair or quarantine generated placeholder modules with invalid syntax.
- 4. Re-run syntax audit until zero active-runtime syntax failures.
- 5. Only then wire dashboard to one canonical payload API.
- 6. Build dashboard panels around runtime summary, 30-stage state, route selection, web evidence, quality gates, operator review.

## Decision
Do not continue feature builds. Repair structural syntax and create a canonical dashboard payload bridge first.
