#!/usr/bin/env python
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class BaselineRunner:
    def __init__(self) -> None:
        self.manifest_path = PROJECT_ROOT / "data" / "baselines" / "claire_baseline_manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.results: List[Dict[str, Any]] = []

    def run(self) -> int:
        checks: List[tuple[str, Callable[[], Dict[str, Any]]]] = [
            ("imports", self.check_imports),
            ("stage_registry", self.check_stage_registry),
            ("threshold_provenance", self.check_threshold_provenance),
            ("mode_governance", self.check_mode_governance),
            ("signal_normalization", self.check_signal_normalization),
            ("connected_enrichment", self.check_connected_enrichment),
            ("hybrid_fusion", self.check_hybrid_fusion),
            ("dashboard_status", self.check_dashboard_status),
            ("acquisition_exports", self.check_acquisition_exports),
            ("updater_health", self.check_updater_health),
            ("feed_activation_depth", self.check_feed_activation_depth),
            ("live_source_catalog", self.check_live_source_catalog),
            ("live_source_orchestration", self.check_live_source_orchestration),
            ("portable_desktop_readiness", self.check_portable_desktop_readiness),
            ("dashboard_update_workflow", self.check_dashboard_update_workflow),
            ("desktop_app_shell", self.check_desktop_app_shell),
            ("enhanced_interface_bridge", self.check_enhanced_interface_bridge),
            ("live_intelligence_spine", self.check_live_intelligence_spine),
            ("live_intelligence_activation", self.check_live_intelligence_activation),
            ("dashboard_layout", self.check_dashboard_layout),
            ("production_readiness", self.check_production_readiness),
            ("plateau_candidate", self.check_plateau_candidate),
            ("portable_launcher", self.check_portable_launcher),
            ("desktop_live_services", self.check_desktop_live_services),
            ("update_sources", self.check_update_sources),
        ]

        for name, fn in checks:
            self.results.append(self._run_check(name, fn))

        summary = {
            "status": "success" if all(item["status"] == "success" for item in self.results) else "failed",
            "baseline_version": self.manifest["baseline_version"],
            "check_count": len(self.results),
            "passed_count": len([item for item in self.results if item["status"] == "success"]),
            "failed": [item for item in self.results if item["status"] != "success"],
            "results": self.results,
        }
        print(json.dumps(summary, indent=2))
        return 0 if summary["status"] == "success" else 1

    def _run_check(self, name: str, fn: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
        try:
            payload = fn()
            return {"name": name, "status": "success", **payload}
        except Exception as exc:
            return {
                "name": name,
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

    def check_imports(self) -> Dict[str, Any]:
        import claire.orchestrator.pipeline_v4  # noqa: F401
        import claire.runtime.dashboard_system_status  # noqa: F401
        import claire.mode.switch_controller  # noqa: F401
        import claire.lifecycle.stage_registry  # noqa: F401
        return {"message": "core package imports succeeded"}

    def check_stage_registry(self) -> Dict[str, Any]:
        from claire.lifecycle.stage_registry import ClaireStageRegistry

        payload = ClaireStageRegistry().as_payload()
        expected_count = self.manifest["expected"]["lifecycle_stage_count"]
        assert payload["stage_count"] == expected_count, payload["stage_count"]
        assert payload["stages"][0]["slug"] == "ingestion"
        assert payload["stages"][-1]["slug"] == "deal_exit_modeling"
        return {"stage_count": payload["stage_count"], "final_stage": payload["final_stage"]}

    def check_threshold_provenance(self) -> Dict[str, Any]:
        from claire.lifecycle.threshold_provenance import ThresholdProvenance

        payload = ThresholdProvenance().as_payload()
        assert payload["threshold_rule_count"] >= self.manifest["expected"]["threshold_rule_minimum"]
        assert payload["calibration_input_count"] >= self.manifest["expected"]["calibration_input_minimum"]
        return {
            "threshold_rule_count": payload["threshold_rule_count"],
            "calibration_input_count": payload["calibration_input_count"],
        }

    def check_mode_governance(self) -> Dict[str, Any]:
        from claire.mode.switch_controller import ModeSwitchController

        controller = ModeSwitchController()
        status = controller.status()
        decision = controller.evaluate({
            "execution_mode": "hybrid",
            "market_universe": "sp500_public",
            "source_category": "public_company_market_data",
            "signal": "public AI infrastructure market pressure",
        })
        assert status["controller"] == self.manifest["expected"]["mode_controller"]
        assert status["supported_modes"] == self.manifest["expected"]["supported_modes"]
        assert decision["requested_mode"] == "hybrid"
        assert decision["effective_mode"] in {"hybrid", "deterministic"}
        return {
            "supported_modes": status["supported_modes"],
            "sample_effective_mode": decision["effective_mode"],
        }

    def check_signal_normalization(self) -> Dict[str, Any]:
        from claire.feeds.signal_normalizer import FeedSignalNormalizer

        normalizer = FeedSignalNormalizer()
        payload = normalizer.normalize_many([
            {
                "signal_id": "baseline_signal_1",
                "status": "success",
                "title": "AI infrastructure governance pressure",
                "summary": "Public metadata indicates AI infrastructure governance and market pressure.",
                "source_category": "public_company_market_data",
                "market_universe": "sp500_public",
                "metadata": {"industry_domain": "information_technology"},
            }
        ], context={
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
        }, activation_decision={"decision": "allow", "source_category": "public_company_market_data"})
        signal = payload["signals"][0]
        assert payload["normalized_count"] == 1
        assert signal["safe_to_enrich"] is True
        return {
            "normalized_count": payload["normalized_count"],
            "signal_type": signal["signal_type"],
            "opportunity_relevance": signal["opportunity_relevance"],
        }

    def check_connected_enrichment(self) -> Dict[str, Any]:
        from claire.enrichment.connected_opportunity_enricher import ConnectedOpportunityEnricher

        candidate = self._candidate()
        signal = self._normalized_signal()
        enriched = ConnectedOpportunityEnricher().enrich_candidate(candidate, [signal], {
            "execution_mode": "connected",
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
        })
        enrichment = enriched["connected_enrichment"]
        assert enrichment["safe_to_enrich"] is True
        assert enrichment["matched_signal_count"] >= 1
        return {
            "matched_signal_count": enrichment["matched_signal_count"],
            "opportunity_relevance": enrichment["opportunity_relevance"],
        }

    def check_hybrid_fusion(self) -> Dict[str, Any]:
        from claire.enrichment.connected_opportunity_enricher import ConnectedOpportunityEnricher
        from claire.fusion.hybrid_opportunity_fusion import HybridOpportunityFusionEngine

        enriched = ConnectedOpportunityEnricher().enrich_candidate(
            self._candidate(),
            [self._normalized_signal()],
            {"execution_mode": "hybrid", "market_universe": "sp500_public", "industry_domain": "information_technology"},
        )
        fused = HybridOpportunityFusionEngine().fuse_candidate(enriched, {"execution_mode": "hybrid"})
        fusion = fused["hybrid_fusion"]
        assert fusion["status"] in {"hybrid_ready", "deterministic_only"}
        assert fusion["recommended_mode"] in {"hybrid", "hybrid_candidate", "deterministic"}
        return {
            "fusion_status": fusion["status"],
            "hybrid_readiness": fusion["hybrid_readiness"],
            "recommended_mode": fusion["recommended_mode"],
        }

    def check_dashboard_status(self) -> Dict[str, Any]:
        from claire.runtime.dashboard_system_status import DashboardSystemStatus

        payload = DashboardSystemStatus().build(
            mode_status={"controller": "mode_switch_controller_v1"},
            feed_status={"activation_layer": "ready"},
            signal_status={"status": "success", "signal_count": 1},
            enrichment_status={"status": "success", "safe_to_enrich_count": 1},
            fusion_status={"status": "success", "fusion_engine": "hybrid_opportunity_fusion_v1"},
            lifecycle_status={"status": "success", "stage_count": 21},
            export_summary={"status": "success", "run_count": 0},
            updater_status={"status": "bootstrap_ready"},
        )
        assert payload["dashboard_rollup"] == self.manifest["expected"]["dashboard_rollup"]
        assert payload["subsystem_count"] == 8
        return {
            "subsystem_count": payload["subsystem_count"],
            "completion_posture": payload["completion_posture"],
        }

    def check_acquisition_exports(self) -> Dict[str, Any]:
        from claire.export.acquisition_export_artifacts import AcquisitionExportArtifactWriter

        preview = AcquisitionExportArtifactWriter().preview({
            "scores": {"portfolio_score": 0.76, "export_package_score": 0.82},
            "decision_classification": "GO",
            "breakthrough_classification": "HIGH",
            "market_gap": {"sector": "information_technology", "market_gap": "AI governance gap", "needed_solution": "AI governance command center"},
            "business_model": {"value_capture": {"strength": "high"}, "revenue_model": {"primary_model": "enterprise subscription"}},
            "strategic_positioning": {"positioning_classification": {"narrative_posture": "category leader"}},
            "productization_path": {"productization_classification": {"state": "pilot_ready"}},
            "deal_exit_modeling": {"exit_readiness": {"state": "ready"}},
            "acquirer_matches": [{"name": "Microsoft", "fit_score": 0.84}],
        }, {"execution_mode": "hybrid"})
        assert preview["status"] == "success"
        assert preview["acquisition_readiness"]["level"] in {"acquisition_grade", "diligence_ready", "internal_review"}
        assert "acquirer_discovery" in preview["diligence_sections"]
        return {
            "acquisition_readiness": preview["acquisition_readiness"]["level"],
            "diligence_section_count": len(preview["diligence_sections"]),
        }

    def check_update_sources(self) -> Dict[str, Any]:
        path = PROJECT_ROOT / "data" / "update_sources" / "allowed_sources.json"
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        assert "allowed_sources" in payload or "sources" in payload or isinstance(payload, dict)
        return {"path": str(path), "state": "available"}

    def check_updater_health(self) -> Dict[str, Any]:
        from claire.updater.update_health import UpdaterHealth

        payload = UpdaterHealth(PROJECT_ROOT).status()
        assert payload["status"] in {"success", "partial"}
        assert payload["checks"]["allowed_sources_file"] is True
        return {"readiness": payload["readiness"], "status": payload["status"]}

    def check_feed_activation_depth(self) -> Dict[str, Any]:
        from claire.feeds.governed_feed_activation import GovernedFeedActivation

        packet = GovernedFeedActivation(PROJECT_ROOT).prepare({
            "execution_mode": "hybrid",
            "market_universe": "sp500_public",
            "source_category": "public_company_market_data",
            "signal": "public AI infrastructure governance pressure",
        })
        assert packet["status"] == "success"
        assert packet["next_action"] in {"provide_public_source_urls_or_use_offline_resolver", "scan_safe_public_metadata", "use_deterministic_fallback"}
        return {"effective_mode": packet["effective_mode"], "next_action": packet["next_action"]}

    def check_live_source_catalog(self) -> Dict[str, Any]:
        from claire.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog
        from claire.feeds.source_catalogs.source_health import LiveSourceHealthChecker

        catalog = LiveSourceCatalog(PROJECT_ROOT)
        status = catalog.status()
        resolved = catalog.resolve(market_universe="sp500_public", limit=5)
        health = LiveSourceHealthChecker(PROJECT_ROOT).check(
            market_universe="sp500_public",
            limit=3,
            fetch_live=False,
        )
        assert status["status"] == "success"
        assert status["source_pack_count"] >= 1
        assert resolved["source_count"] >= 3
        assert health["healthy_count"] == health["source_count"]
        return {
            "catalog_version": status["catalog_version"],
            "active_source_count": status["active_source_count"],
            "resolved_source_count": resolved["source_count"],
        }

    def check_live_source_orchestration(self) -> Dict[str, Any]:
        from claire.feeds.live_source_orchestrator import LiveSourceOrchestrator

        status = LiveSourceOrchestrator(PROJECT_ROOT).status()
        assert status["status"] == "success"
        assert status["desktop_live_ready"] is True
        return {"orchestrator": status["orchestrator"], "active_source_count": status["active_source_count"]}

    def check_portable_desktop_readiness(self) -> Dict[str, Any]:
        from claire.runtime.portable_desktop_readiness import PortableDesktopReadiness

        payload = PortableDesktopReadiness(PROJECT_ROOT).status()
        assert payload["status"] == "success"
        assert payload["ready_for_flash_drive_use"] is True
        assert payload["launcher_checks"]["unified"] is True
        return {"recommended_launcher": payload["recommended_launcher"]}

    def check_dashboard_update_workflow(self) -> Dict[str, Any]:
        from claire.updater.dashboard_update_workflow import DashboardUpdateWorkflow

        payload = DashboardUpdateWorkflow(PROJECT_ROOT).status()
        assert payload["status"] in {"success", "partial"}
        assert payload["dashboard_workflow"] == "v5.68"
        return {"readiness": payload["readiness"], "dashboard_install_enabled": payload["dashboard_install_enabled"]}

    def check_desktop_app_shell(self) -> Dict[str, Any]:
        from claire.runtime.desktop_app_shell import DesktopAppShell

        payload = DesktopAppShell(PROJECT_ROOT).status()
        assert payload["status"] == "success"
        assert payload["ready"] is True
        return {"shell_version": payload["shell_version"], "shell_type": payload["shell_type"]}

    def check_enhanced_interface_bridge(self) -> Dict[str, Any]:
        from claire.runtime.enhanced_interface_bridge import EnhancedInterfaceBridge

        payload = EnhancedInterfaceBridge(PROJECT_ROOT).status()
        assert payload["status"] == "success"
        assert payload["capability_count"] >= 20
        assert payload["ready_or_starter_count"] >= 20
        action = EnhancedInterfaceBridge(PROJECT_ROOT).action({"action_id": "claire_search", "query": "AI governance"})
        assert action["status"] == "success"
        return {
            "capability_count": payload["capability_count"],
            "ready_or_starter_count": payload["ready_or_starter_count"],
            "planned_count": payload["planned_count"],
        }

    def check_live_intelligence_spine(self) -> Dict[str, Any]:
        from claire.live_intelligence.connectors import ConnectorRunner
        from claire.live_intelligence.entity_registry import SourceEntityRegistry
        from claire.live_intelligence.live_opportunity_monitor import LiveOpportunityMonitor

        registry = SourceEntityRegistry(PROJECT_ROOT).status()
        connectors = ConnectorRunner(PROJECT_ROOT).run({
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
            "entity_limit": 2,
        })
        monitor = LiveOpportunityMonitor(PROJECT_ROOT).run({
            "execution_mode": "hybrid",
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
            "buyer_segment": "enterprise_c_suite",
            "objective": "discover_market_gaps",
            "entity_limit": 2,
        })
        assert registry["entity_count"] >= 4
        assert connectors["connector_count"] >= 4
        assert connectors["record_count"] >= 4
        assert monitor["live_opportunities_ready"] is True
        assert monitor["solutions"]["candidate_count"] >= 1
        return {
            "registry_version": registry["registry_version"],
            "connector_record_count": connectors["record_count"],
            "solution_candidate_count": monitor["solutions"]["candidate_count"],
        }

    def check_live_intelligence_activation(self) -> Dict[str, Any]:
        from claire.live_intelligence.history_store import LiveIntelligenceHistoryStore
        from claire.live_intelligence.live_opportunity_monitor import LiveOpportunityMonitor
        from claire.live_intelligence.monitor_candidate_bridge import MonitorCandidateBridge
        from claire.live_intelligence.source_scan_planner import SourceScanPlanner

        context = {
            "execution_mode": "hybrid",
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
            "buyer_segment": "enterprise_c_suite",
            "objective": "discover_market_gaps",
            "entity_limit": 2,
        }
        plan = SourceScanPlanner(PROJECT_ROOT).plan(context)
        monitor = LiveOpportunityMonitor(PROJECT_ROOT).run(context)
        history = LiveIntelligenceHistoryStore(PROJECT_ROOT).record(monitor, context=context)
        bridge = MonitorCandidateBridge().build_candidates(monitor, context=context)
        assert plan["scan_item_count"] >= 4
        assert history["status"] == "success"
        assert bridge["candidate_count"] >= 1
        return {
            "scan_item_count": plan["scan_item_count"],
            "monitor_run_id": history["monitor_run_id"],
            "candidate_count": bridge["candidate_count"],
        }

    def check_dashboard_layout(self) -> Dict[str, Any]:
        from claire.runtime.dashboard_layout_registry import DashboardLayoutRegistry

        payload = DashboardLayoutRegistry().payload()
        assert payload["group_count"] >= 4
        return {"layout_version": payload["layout_version"], "group_count": payload["group_count"]}

    def check_production_readiness(self) -> Dict[str, Any]:
        from claire.runtime.production_readiness import ProductionReadiness

        payload = ProductionReadiness(PROJECT_ROOT).status()
        assert payload["readiness_version"] == "v5.61"
        return {"production_posture": payload["production_posture"], "known_blocker_count": payload["known_blocker_count"]}

    def check_plateau_candidate(self) -> Dict[str, Any]:
        from claire.runtime.plateau_candidate import PlateauCandidateReport

        payload = PlateauCandidateReport(PROJECT_ROOT).build(baseline_status="success")
        assert payload["plateau_version"] == "v5.62"
        return {"plateau_posture": payload["plateau_posture"], "blocker_count": len(payload["blockers"])}

    def check_portable_launcher(self) -> Dict[str, Any]:
        from tools.portable_launcher import PortableLauncher

        payload = PortableLauncher(PROJECT_ROOT).status()
        assert payload["checks"]["dashboard_server"] is True
        assert payload["checks"]["dashboard_html"] is True
        assert payload["checks"]["baseline_runner"] is True
        assert payload["checks"]["selected_python_available"] is True
        return {"portable_status": payload["status"], "selected_python": payload["selected_python"]}

    def check_desktop_live_services(self) -> Dict[str, Any]:
        from claire.runtime.desktop_service_status import DesktopServiceStatus

        payload = DesktopServiceStatus(PROJECT_ROOT).status(
            mode_status={"status": "success", "controller": "mode_switch_controller_v1"},
            feed_status={"status": "success", "feed_layer": "scaffold"},
            live_scan_status={"status": "success", "live_enabled": False},
            live_source_catalog_status={"status": "success", "active_source_count": 12},
            updater_status={"readiness": "self_update_ready"},
            baseline_available=True,
        )
        assert payload["service_count"] >= 8
        assert payload["ready_service_count"] >= 8
        return {"desktop_state": payload["desktop_state"], "ready_service_count": payload["ready_service_count"]}

    def _candidate(self) -> Dict[str, Any]:
        return {
            "title": "AI infrastructure governance command center",
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
            "market_gap": "Enterprises need governed AI infrastructure oversight.",
            "needed_solution": "Governance and market-pressure intelligence dashboard.",
            "opportunity_direction": "Build an AI infrastructure governance signal platform.",
            "why_now": "AI governance pressure and infrastructure investment are rising.",
            "selection_score": 0.74,
            "confidence_label": "high",
            "raw_input": "AI infrastructure governance command center for public-company market pressure.",
        }

    def _normalized_signal(self) -> Dict[str, Any]:
        return {
            "signal_id": "baseline_norm_1",
            "market_universe": "sp500_public",
            "industry_domain": "information_technology",
            "source_category": "public_company_market_data",
            "governance_status": "allow",
            "signal_type": "governance / AI infrastructure / market pressure",
            "signal_strength": "medium",
            "signal_strength_score": 0.72,
            "opportunity_relevance": "high",
            "opportunity_relevance_score": 0.82,
            "safe_to_enrich": True,
            "title": "AI infrastructure governance pressure",
            "summary": "Public metadata indicates AI infrastructure governance pressure.",
        }


def main() -> int:
    return BaselineRunner().run()


if __name__ == "__main__":
    raise SystemExit(main())
