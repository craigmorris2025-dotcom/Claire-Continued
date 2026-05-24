#!/usr/bin/env python
from __future__ import annotations
import argparse, json, mimetypes, sys, traceback, webbrowser, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

def find_project_root(start=None):
    start=(start or Path.cwd()).resolve()
    for c in [start]+list(start.parents):
        if (c/"main.py").exists() and (c/"src"/"claire").exists(): return c
    raise SystemExit("Could not detect Claire project root.")

PROJECT_ROOT=find_project_root(); SRC=PROJECT_ROOT/"src"
for p in (SRC, PROJECT_ROOT):
    if str(p) not in sys.path: sys.path.insert(0,str(p))

from runtime_core.domain.contract import ContractValidator
from runtime_core.orchestrator.pipeline_v4 import PipelineOrchestrator
from runtime_core.runtime.export_browser import ExportBrowser
from runtime_core.runtime.run_history import RunHistory
from runtime_core.runtime.run_events import RUN_EVENTS
from runtime_core.runtime.command_catalog import OpportunityCommandCatalog
from runtime_core.runtime.market_universe_taxonomy import MarketUniverseTaxonomy
from runtime_core.runtime.search_suggestions import OpportunitySearchSuggestions
from runtime_core.runtime.opportunity_seed_generator import OpportunitySeedGenerator
from runtime_core.runtime.opportunity_candidate_store import OPPORTUNITY_CANDIDATES
from runtime_core.runtime.dashboard_system_status import DashboardSystemStatus
from runtime_core.runtime.dashboard_layout_registry import DashboardLayoutRegistry
from runtime_core.runtime.stale_path_audit import StalePathAudit
from runtime_core.runtime.production_readiness import ProductionReadiness
from runtime_core.runtime.plateau_candidate import PlateauCandidateReport
from runtime_core.runtime.desktop_service_status import DesktopServiceStatus
from runtime_core.runtime.portable_desktop_readiness import PortableDesktopReadiness
from runtime_core.runtime.desktop_app_shell import DesktopAppShell
from runtime_core.runtime.enhanced_interface_bridge import EnhancedInterfaceBridge
from runtime_core.enrichment.connected_opportunity_enricher import ConnectedOpportunityEnricher
from runtime_core.fusion.hybrid_opportunity_fusion import HybridOpportunityFusionEngine
from runtime_core.export.connected_export_artifacts import ConnectedExportArtifactWriter
from runtime_core.export.acquisition_export_artifacts import AcquisitionExportArtifactWriter
from runtime_core.lifecycle.stage_registry import ClaireStageRegistry
from runtime_core.lifecycle.threshold_provenance import ThresholdProvenance
from runtime_core.mode.switch_controller import ModeSwitchController
from runtime_core.mode.state_manager import ModeStateManager
from runtime_core.mode.isolation_layer import ModeIsolationLayer
from runtime_core.feeds.feed_registry import FeedRegistry
from runtime_core.feeds.source_catalogs.public_company_sources import PublicCompanySourceCatalog
from runtime_core.feeds.source_catalogs.index_universe_registry import IndexUniverseRegistry
from runtime_core.feeds.source_catalogs.offline_universe_resolver import OfflinePublicCompanyUniverseResolver
from runtime_core.feeds.source_catalogs.live_source_catalog import LiveSourceCatalog
from runtime_core.feeds.source_catalogs.source_health import LiveSourceHealthChecker
from runtime_core.feeds.public_company_live_scan import PublicCompanyLiveScan
from runtime_core.feeds.live_source_orchestrator import LiveSourceOrchestrator
from runtime_core.feeds.governed_feed_activation import GovernedFeedActivation
from runtime_core.feeds.signal_normalizer import FeedSignalNormalizer
from runtime_core.feeds.signal_registry import SIGNAL_REGISTRY
from runtime_core.governance.redline_classifier import RedlineClassifier
from runtime_core.governance.legal_audit_log import LegalAuditLog
from runtime_core.governance.feed_activation_policy import FeedActivationPolicy
from runtime_core.governance.feed_audit_log import FeedAuditLog
from runtime_core.updater.update_health import UpdaterHealth
from runtime_core.updater.dashboard_update_workflow import DashboardUpdateWorkflow
from runtime_core.live_intelligence.entity_registry import SourceEntityRegistry
from runtime_core.live_intelligence.connectors import ConnectorRunner
from runtime_core.live_intelligence.signal_extraction import SignalExtractionWorker
from runtime_core.live_intelligence.trend_clustering import TrendClusterer
from runtime_core.live_intelligence.gap_detection import GapDetectionEngine
from runtime_core.live_intelligence.solution_synthesis import SolutionSynthesisEngine
from runtime_core.live_intelligence.live_opportunity_monitor import LiveOpportunityMonitor
from runtime_core.live_intelligence.history_store import LiveIntelligenceHistoryStore
from runtime_core.live_intelligence.source_scan_planner import SourceScanPlanner
from runtime_core.live_intelligence.monitor_candidate_bridge import MonitorCandidateBridge
from runtime_core.scan.scan_continuation import ScanContinuationRunner
from runtime_core.research import ResearchService

DASHBOARD_DIR=PROJECT_ROOT/"src"/"frontend"/"export_dashboard"
CATALOG=OpportunityCommandCatalog()
TAXONOMY=MarketUniverseTaxonomy()
SUGGESTIONS=OpportunitySearchSuggestions()
SEEDS=OpportunitySeedGenerator()
DASHBOARD_STATUS=DashboardSystemStatus()
DASHBOARD_LAYOUT=DashboardLayoutRegistry()
DESKTOP_SERVICES=DesktopServiceStatus(PROJECT_ROOT)
PORTABLE_READINESS=PortableDesktopReadiness(PROJECT_ROOT)
DESKTOP_APP_SHELL=DesktopAppShell(PROJECT_ROOT)
ENHANCED_INTERFACE=EnhancedInterfaceBridge(PROJECT_ROOT)
ENRICHER=ConnectedOpportunityEnricher()
HYBRID_FUSION=HybridOpportunityFusionEngine()
CONNECTED_EXPORTS=ConnectedExportArtifactWriter()
ACQUISITION_EXPORTS=AcquisitionExportArtifactWriter()
STAGE_REGISTRY=ClaireStageRegistry()
THRESHOLD_PROVENANCE=ThresholdProvenance()
MODE_SWITCH=ModeSwitchController()
MODE_STATE=ModeStateManager()
MODE_ISOLATION=ModeIsolationLayer()
FEEDS=FeedRegistry()
PUBLIC_COMPANY_SOURCES=PublicCompanySourceCatalog()
INDEX_UNIVERSES=IndexUniverseRegistry()
OFFLINE_UNIVERSE_RESOLVER=OfflinePublicCompanyUniverseResolver()
LIVE_SOURCE_CATALOG=LiveSourceCatalog(PROJECT_ROOT)
LIVE_SOURCE_HEALTH=LiveSourceHealthChecker(PROJECT_ROOT)
PUBLIC_COMPANY_LIVE_SCAN=PublicCompanyLiveScan()
LIVE_SOURCE_ORCHESTRATOR=LiveSourceOrchestrator(PROJECT_ROOT)
GOVERNED_FEED_ACTIVATION=GovernedFeedActivation(PROJECT_ROOT)
SIGNAL_NORMALIZER=FeedSignalNormalizer()
GOVERNANCE=RedlineClassifier()
LEGAL_AUDIT=LegalAuditLog()
FEED_POLICY=FeedActivationPolicy()
FEED_AUDIT=FeedAuditLog()
UPDATE_WORKFLOW=DashboardUpdateWorkflow(PROJECT_ROOT)
SOURCE_ENTITY_REGISTRY=SourceEntityRegistry(PROJECT_ROOT)
LIVE_CONNECTORS=ConnectorRunner(PROJECT_ROOT)
SIGNAL_EXTRACTOR=SignalExtractionWorker()
TREND_CLUSTERER=TrendClusterer()
GAP_DETECTOR=GapDetectionEngine()
SOLUTION_SYNTHESIZER=SolutionSynthesisEngine()
LIVE_OPPORTUNITY_MONITOR=LiveOpportunityMonitor(PROJECT_ROOT)
LIVE_HISTORY=LiveIntelligenceHistoryStore(PROJECT_ROOT)
SOURCE_SCAN_PLANNER=SourceScanPlanner(PROJECT_ROOT)
MONITOR_CANDIDATE_BRIDGE=MonitorCandidateBridge()
SCAN_CONTINUATION=ScanContinuationRunner()
RESEARCH_SERVICE=ResearchService()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print("[dashboard]", fmt % args)
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path
        try:
            if path in {"/","/index.html"}: return self.file(DASHBOARD_DIR/"index.html")
            if path in {"/dashboard.css","/dashboard.js"}: return self.file(DASHBOARD_DIR/path.lstrip("/"))
            if path.startswith("/discover/"):
                filename=Path(unquote(path)).name
                allowed={"DiscoverPipeline.js","SignalPanel.js","ClusterPanel.js","GapPanel.js","SolutionPanel.js"}
                if filename in allowed: return self.file(PROJECT_ROOT/"src"/"frontend"/"discover"/filename)
                return self.send_error(404,"Unsupported Discover component")
            if path.startswith("/monitor/"):
                filename=Path(unquote(path)).name
                allowed={"MonitorSurface.js","MonitorStatusBar.js","MonitorTimeline.js","MonitorDetailPanel.js"}
                if filename in allowed: return self.file(PROJECT_ROOT/"src"/"frontend"/"monitor"/filename)
                return self.send_error(404,"Unsupported Monitor component")
            if path=="/api/health": return self.json(self.health())
            if path=="/api/commands": return self.json(CATALOG.catalog())
            if path=="/api/market-universe": return self.json(TAXONOMY.catalog())
            if path=="/api/feeds/status": return self.json(FEEDS.status())
            if path=="/api/feeds/public-company-sources": return self.json(PUBLIC_COMPANY_SOURCES.catalog())
            if path=="/api/feeds/live-source-catalog/status": return self.json(LIVE_SOURCE_CATALOG.status())
            if path=="/api/feeds/live-source-catalog/packs": return self.json(LIVE_SOURCE_CATALOG.packs())
            if path=="/api/feeds/live-source-catalog/health": return self.json(LIVE_SOURCE_HEALTH.snapshot())
            if path=="/api/feeds/live-orchestration/status": return self.json(LIVE_SOURCE_ORCHESTRATOR.status())
            if path=="/api/feeds/public-company-live/status": return self.json(PUBLIC_COMPANY_LIVE_SCAN.status())
            if path=="/api/signals/status": return self.json(SIGNAL_REGISTRY.status())
            if path=="/api/signals/normalized": return self.json(SIGNAL_REGISTRY.list())
            if path=="/api/opportunities/enrichment-status": return self.json(self.enrichment_status())
            if path=="/api/opportunities/fusion-status": return self.json(self.fusion_status())
            if path=="/api/lifecycle/stage-registry": return self.json(STAGE_REGISTRY.as_payload())
            if path=="/api/lifecycle/threshold-provenance": return self.json(THRESHOLD_PROVENANCE.as_payload())
            if path=="/api/modes/status": return self.json(self.mode_status())
            if path=="/api/modes/recent": return self.json(MODE_STATE.recent())
            if path=="/api/dashboard/system-status": return self.json(self.dashboard_system_status())
            if path=="/api/services/status": return self.json(self.services_status())
            if path=="/api/dashboard/layout": return self.json(DASHBOARD_LAYOUT.payload())
            if path=="/api/system/stale-path-audit": return self.json(StalePathAudit(PROJECT_ROOT).run())
            if path=="/api/system/production-readiness": return self.json(ProductionReadiness(PROJECT_ROOT).status())
            if path=="/api/system/plateau-candidate": return self.json(PlateauCandidateReport(PROJECT_ROOT).build())
            if path=="/api/updater/status": return self.json(UpdaterHealth(PROJECT_ROOT).status())
            if path=="/api/updater/dashboard-status": return self.json(UPDATE_WORKFLOW.status())
            if path=="/api/updater/rollbacks": return self.json(UPDATE_WORKFLOW.rollbacks())
            if path=="/api/portable/status": return self.json(PORTABLE_READINESS.status())
            if path=="/api/desktop-app/status": return self.json(DESKTOP_APP_SHELL.status())
            if path=="/api/enhanced-interface/status": return self.json(ENHANCED_INTERFACE.status())
            if path=="/api/live-intelligence/status": return self.json(self.live_intelligence_status())
            if path=="/api/live-intelligence/entities": return self.json(SOURCE_ENTITY_REGISTRY.status())
            if path=="/api/live-intelligence/connectors/status": return self.json(LIVE_CONNECTORS.status())
            if path=="/api/live-intelligence/monitor/status": return self.json(LIVE_OPPORTUNITY_MONITOR.status())
            if path=="/api/live-intelligence/history": return self.json(LIVE_HISTORY.list())
            if path=="/api/live-intelligence/latest": return self.json(LIVE_HISTORY.latest())
            if path=="/api/live-intelligence/scan-plan": return self.json(SOURCE_SCAN_PLANNER.plan())
            if path=="/api/feeds/governed-activation/status": return self.json(GOVERNED_FEED_ACTIVATION.status())
            if path=="/api/feeds/index-universes": return self.json(INDEX_UNIVERSES.all())
            if path=="/api/feeds/offline-universe/status": return self.json(OFFLINE_UNIVERSE_RESOLVER.status())
            if path=="/api/feeds/activation-status": return self.json(FEED_POLICY.status())
            if path=="/api/feeds/audit": return self.json(FEED_AUDIT.recent())
            if path=="/api/governance/audit": return self.json(LEGAL_AUDIT.recent())
            if path=="/api/runs": return self.json(ExportBrowser().list_runs(limit=200,rescan_if_empty=True))
            if path=="/api/research/evidence": return self.json(RESEARCH_SERVICE.evidence())
            if path=="/api/summary": return self.json(ExportBrowser().summary())
            if path=="/api/events": return self.json(RUN_EVENTS.list())
            if path.startswith("/api/events/"): return self.events(path,parse_qs(parsed.query))
            if path.startswith("/api/runs/"): return self.run_api(path,parse_qs(parsed.query))
            self.send_error(404,"Not found")
        except Exception as e:
            self.json({"status":"error","error":str(e),"traceback":traceback.format_exc()},500)
    def do_POST(self):
        parsed=urlparse(self.path)
        try:
            if parsed.path=="/api/governance/evaluate": return self.json(self.governance_evaluate(self.body()))
            if parsed.path=="/api/modes/evaluate": return self.json(self.mode_evaluate(self.body()))
            if parsed.path=="/api/feeds/activation-check": return self.json(self.feed_activation_check(self.body()))
            if parsed.path=="/api/feeds/governed-activation/prepare": return self.json(GOVERNED_FEED_ACTIVATION.prepare(self.body()))
            if parsed.path=="/api/feeds/offline-universe/resolve": return self.json(self.resolve_offline_universe(self.body()))
            if parsed.path=="/api/feeds/live-source-catalog/resolve": return self.json(self.resolve_live_source_catalog(self.body()))
            if parsed.path=="/api/feeds/live-source-catalog/health-check": return self.json(self.check_live_source_health(self.body()))
            if parsed.path=="/api/feeds/live-orchestration/run": return self.json(self.run_live_orchestration(self.body()))
            if parsed.path=="/api/feeds/public-company-live/scan": return self.json(self.public_company_live_scan(self.body()))
            if parsed.path=="/api/signals/normalize": return self.json(self.normalize_signals(self.body()))
            if parsed.path=="/api/feeds/scan": return self.json(self.scan_feed(self.body()))
            if parsed.path=="/api/rescan": return self.json(RunHistory().rescan_exports("exports"))
            if parsed.path=="/api/evaluate": return self.json(self.eval_sync(self.body()))
            if parsed.path=="/api/evaluate/async": return self.json(self.eval_async(self.body()))
            if parsed.path=="/api/research/search":
                payload=self.body(); return self.json(RESEARCH_SERVICE.search(payload.get("query",""),payload.get("scope","all"),payload.get("limit",20)))
            if parsed.path=="/api/research/evidence/add":
                payload=self.body(); return self.json(RESEARCH_SERVICE.add_evidence(payload.get("result") or {},payload.get("notes","")))
            if parsed.path=="/api/research/evidence/clear": return self.json(RESEARCH_SERVICE.clear_evidence())
            if parsed.path=="/api/research/evidence/pipeline-input": return self.json(RESEARCH_SERVICE.evidence_pipeline_input())
            if parsed.path=="/api/research/send-to-pipeline":
                payload=self.body(); return self.json(RESEARCH_SERVICE.send_to_pipeline(payload.get("result") or {},payload.get("route","scan")))
            if parsed.path=="/api/opportunities/search-needed-solutions": return self.json(self.search_needed_solutions(self.body()))
            if parsed.path=="/api/opportunities/generate": return self.json(self.generate_public_opportunities(self.body()))
            if parsed.path=="/api/opportunities/enrich-preview": return self.json(self.enrich_preview(self.body()))
            if parsed.path=="/api/opportunities/fusion-preview": return self.json(self.fusion_preview(self.body()))
            if parsed.path=="/api/exports/acquisition-preview": return self.json(ACQUISITION_EXPORTS.preview(self.body()))
            if parsed.path=="/api/updater/preview": return self.json(self.updater_preview(self.body()))
            if parsed.path=="/api/updater/install": return self.json(self.updater_install(self.body()))
            if parsed.path=="/api/enhanced-interface/action": return self.json(self.enhanced_interface_action(self.body()))
            if parsed.path=="/api/live-intelligence/connectors/run": return self.json(LIVE_CONNECTORS.run(self.body()))
            if parsed.path=="/api/live-intelligence/extract": return self.json(self.live_extract(self.body()))
            if parsed.path=="/api/live-intelligence/cluster": return self.json(TREND_CLUSTERER.cluster(self.body()))
            if parsed.path=="/api/live-intelligence/detect-gaps": return self.json(GAP_DETECTOR.detect(self.body()))
            if parsed.path=="/api/live-intelligence/synthesize": return self.json(SOLUTION_SYNTHESIZER.synthesize(self.body(), self.body()))
            if parsed.path=="/api/live-intelligence/monitor/run": return self.json(self.live_monitor_run(self.body()))
            if parsed.path=="/api/live-intelligence/scan-plan": return self.json(SOURCE_SCAN_PLANNER.plan(self.body()))
            if parsed.path=="/api/live-intelligence/activate-candidates": return self.json(self.activate_live_candidates(self.body()))
            if parsed.path=="/api/opportunities/run-candidate": return self.json(self.run_candidate(self.body()))
            self.send_error(404,"Not found")
        except Exception as e:
            self.json({"status":"error","error":str(e),"traceback":traceback.format_exc()},500)
    def governance_evaluate(self,payload):
        text=(payload.get("raw_input") or payload.get("signal") or payload.get("text") or "")
        context={
            "workflow":payload.get("workflow"),
            "execution_mode":payload.get("execution_mode"),
            "market_universe":payload.get("market_universe"),
            "industry_domain":payload.get("industry_domain"),
            "buyer_segment":payload.get("buyer_segment"),
            "objective":payload.get("objective"),
        }
        decision=GOVERNANCE.classify(text,context)
        audit=LEGAL_AUDIT.log("governance_evaluation",decision,context)
        return {"status":"success","decision":decision,"audit_event":audit}
    def health(self):
        return {
            "status":"success",
            "service":"claire_export_dashboard",
            "project_root":str(PROJECT_ROOT),
            "dashboard_dir":str(DASHBOARD_DIR),
            "portable":True,
            "desktop_live":bool(__import__("os").environ.get("PLATFORM_DESKTOP_LIVE","").strip()=="1"),
            "app_shell":bool(__import__("os").environ.get("PLATFORM_APP_SHELL","").strip()=="1"),
            "live_connected_enabled":bool(__import__("os").environ.get("PLATFORM_ENABLE_LIVE_FEEDS","").strip()=="1"),
            "baseline_runner":(PROJECT_ROOT/"tools"/"run_claire_baseline.py").exists(),
            "updater_status":UpdaterHealth(PROJECT_ROOT).status().get("readiness"),
        }
    def mode_status(self):
        status=MODE_SWITCH.status()
        status["recent"]=MODE_STATE.recent(limit=5)
        return status
    def mode_evaluate(self,payload):
        decision=MODE_SWITCH.evaluate(payload)
        event=MODE_STATE.record("mode_evaluation",decision,{
            "workflow":payload.get("workflow"),
            "market_universe":payload.get("market_universe"),
            "industry_domain":payload.get("industry_domain"),
        })
        return {"status":decision.get("status","success"),"mode_decision":decision,"mode_event":event}
    def dashboard_system_status(self):
        return DASHBOARD_STATUS.build(
            mode_status=MODE_SWITCH.status(),
            feed_status=FEED_POLICY.status(),
            signal_status=SIGNAL_REGISTRY.status(),
            enrichment_status=self.enrichment_status(),
            fusion_status=self.fusion_status(),
            lifecycle_status=STAGE_REGISTRY.summary(),
            export_summary=ExportBrowser().summary(),
            updater_status=UpdaterHealth(PROJECT_ROOT).status(),
        )
    def services_status(self):
        return DESKTOP_SERVICES.status(
            mode_status=MODE_SWITCH.status(),
            feed_status=FEEDS.status(),
            live_scan_status=PUBLIC_COMPANY_LIVE_SCAN.status(),
            live_source_catalog_status=LIVE_SOURCE_CATALOG.status(),
            updater_status=UpdaterHealth(PROJECT_ROOT).status(),
            baseline_available=(PROJECT_ROOT/"tools"/"run_claire_baseline.py").exists(),
        )
    def public_company_live_scan(self,payload):
        mode_decision=MODE_SWITCH.evaluate(payload)
        MODE_STATE.record("public_company_live_scan",mode_decision,{"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision,"activation_decision":mode_decision.get("feed_activation")}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        activation=mode_decision.get("feed_activation") or FEED_POLICY.evaluate(payload)
        FEED_AUDIT.log("public_company_live_scan_v1",activation,payload)
        if activation.get("decision")=="block":
            return {"status":"blocked","activation_decision":activation}
        result = PUBLIC_COMPANY_LIVE_SCAN.scan(
            market_universe=payload.get("market_universe","sp500_public"),
            execution_mode=payload.get("execution_mode","connected"),
            activation_decision=activation,
            source_urls=payload.get("source_urls",[]),
            catalog_limit=int(payload.get("catalog_limit",5) or 5),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            signal=payload.get("signal",""),
        )
        normalized = SIGNAL_NORMALIZER.normalize_many(
            result.get("signals", []),
            context=payload,
            activation_decision=activation,
        )
        SIGNAL_REGISTRY.put_many(normalized.get("signals", []))
        result["normalized_signals"] = normalized.get("signals", [])
        result["normalized_summary"] = normalized.get("summary", {})
        result["normalization_status"] = normalized.get("status")
        result["mode_decision"] = mode_decision
        return result
    def normalize_signals(self,payload):
        activation=payload.get("activation_decision") or FEED_POLICY.evaluate(payload)
        normalized=SIGNAL_NORMALIZER.normalize_many(
            payload.get("signals", []),
            context=payload,
            activation_decision=activation,
        )
        SIGNAL_REGISTRY.put_many(normalized.get("signals", []))
        return normalized
    def resolve_offline_universe(self,payload):
        return OFFLINE_UNIVERSE_RESOLVER.resolve(
            market_universe=payload.get("market_universe","sp500_public"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
        )
    def resolve_live_source_catalog(self,payload):
        return LIVE_SOURCE_CATALOG.resolve(
            market_universe=payload.get("market_universe","sp500_public"),
            source_ids=payload.get("source_ids") or [],
            source_types=payload.get("source_types") or [],
            limit=int(payload.get("limit",5) or 5),
        )
    def check_live_source_health(self,payload):
        return LIVE_SOURCE_HEALTH.check(
            market_universe=payload.get("market_universe","sp500_public"),
            limit=int(payload.get("limit",5) or 5),
            fetch_live=bool(payload.get("fetch_live",False)),
        )
    def run_live_orchestration(self,payload):
        mode_decision=MODE_SWITCH.evaluate(payload)
        MODE_STATE.record("live_source_orchestration",mode_decision,{"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision,"activation_decision":mode_decision.get("feed_activation")}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        activation=mode_decision.get("feed_activation") or FEED_POLICY.evaluate(payload)
        FEED_AUDIT.log("live_source_orchestration_v1",activation,payload)
        if activation.get("decision")=="block":
            return {"status":"blocked","activation_decision":activation,"mode_decision":mode_decision}
        result=LIVE_SOURCE_ORCHESTRATOR.run(payload,activation)
        scan=result.get("scan",{})
        normalized = SIGNAL_NORMALIZER.normalize_many(
            scan.get("signals", []),
            context=payload,
            activation_decision=activation,
        )
        SIGNAL_REGISTRY.put_many(normalized.get("signals", []))
        result["normalized_signals"]=normalized.get("signals", [])
        result["normalized_summary"]=normalized.get("summary", {})
        result["normalization_status"]=normalized.get("status")
        result["activation_decision"]=activation
        result["mode_decision"]=mode_decision
        return result
    def updater_preview(self,payload):
        return UPDATE_WORKFLOW.preview(
            url=payload.get("url",""),
            expected_sha256=payload.get("expected_sha256",""),
        )
    def updater_install(self,payload):
        return UPDATE_WORKFLOW.install(
            url=payload.get("url",""),
            expected_sha256=payload.get("expected_sha256",""),
            confirm=bool(payload.get("confirm",False)),
            run_baseline=bool(payload.get("run_baseline",False)),
        )
    def enhanced_interface_action(self,payload):
        action=ENHANCED_INTERFACE.action(payload)
        action_id=payload.get("action_id","")
        if action_id=="claire_search":
            query=payload.get("query") or payload.get("signal") or payload.get("raw_input") or ""
            search_payload=dict(payload)
            search_payload["signal"]=query
            action["needed_solutions"]=self.search_needed_solutions(search_payload)
        elif action_id=="mode_switching":
            action["mode_decision"]=MODE_SWITCH.evaluate(payload)
        elif action_id=="live_discoveries":
            activation=FEED_POLICY.evaluate(payload)
            action["live_orchestration"]=LIVE_SOURCE_ORCHESTRATOR.run(payload,activation)
        return action
    def live_intelligence_status(self):
        registry=SOURCE_ENTITY_REGISTRY.status()
        connectors=LIVE_CONNECTORS.status()
        monitor=LIVE_OPPORTUNITY_MONITOR.status()
        return {
            "status":"success",
            "live_intelligence_version":"v5.81",
            "registry":registry,
            "connectors":connectors,
            "monitor":monitor,
            "completion_chain":[
                "v5.72 source_entity_registry",
                "v5.73 sec_public_filing_connector",
                "v5.74 investor_relations_connector",
                "v5.75 public_news_metadata_connector",
                "v5.76 patent_uspto_connector",
                "v5.77 signal_extraction_workers",
                "v5.78 signal_clustering_trend_formation",
                "v5.79 gap_detection_engine",
                "v5.80 solution_synthesis_engine",
                "v5.81 live_opportunity_monitor",
                "v5.82 monitor_history_store",
                "v5.83 source_freshness_scan_planner",
                "v5.84 live_solution_candidate_activation",
            ],
        }
    def live_extract(self,payload):
        connector_payload=payload.get("connector_payload") or LIVE_CONNECTORS.run(payload)
        return SIGNAL_EXTRACTOR.extract(connector_payload,context=payload)
    def live_monitor_run(self,payload):
        mode_decision=MODE_SWITCH.evaluate(payload)
        MODE_STATE.record("live_opportunity_monitor",mode_decision,{"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision}
        isolated=MODE_ISOLATION.isolate(payload,mode_decision)
        activation=mode_decision.get("feed_activation") or FEED_POLICY.evaluate(isolated)
        FEED_AUDIT.log("live_opportunity_monitor_v1",activation,isolated)
        if activation.get("decision")=="block":
            return {"status":"blocked","activation_decision":activation,"mode_decision":mode_decision}
        continuation=SCAN_CONTINUATION.run_until_result(isolated, LIVE_OPPORTUNITY_MONITOR.run)
        result=continuation.get("last_result") or {}
        history=LIVE_HISTORY.record(result,context=isolated)
        bridge=MONITOR_CANDIDATE_BRIDGE.build_candidates(result,context=isolated)
        public_cards=[]
        for candidate in bridge.get("candidates", [])[:5]:
            candidate_id=OPPORTUNITY_CANDIDATES.put(candidate)
            stored=OPPORTUNITY_CANDIDATES.get(candidate_id) or {}
            public_cards.append(OPPORTUNITY_CANDIDATES.public_card(stored))
        result["activation_decision"]=activation
        result["mode_decision"]=mode_decision
        result["history_record"]=history
        result["activated_candidates"]=public_cards
        result["scan_iterations"]=continuation.get("scan_iterations", [])
        result["terminal_state"]=continuation.get("terminal_state")
        result["terminal_reason"]=continuation.get("terminal_reason")
        result["route_selected"]=continuation.get("route_selected")
        result["core_pipeline_run"]=self.run_scan_pipeline_output(isolated,result,continuation)
        return result
    def run_scan_pipeline_output(self,payload,result,continuation):
        try:
            raw=self.scan_pipeline_input(payload,result,continuation)
            mode=self.normalize_mode(payload.get("execution_mode"))
            intent=ContractValidator().validate_intent({
                "raw_input":raw,
                "mode":mode,
                "request_type":"scan",
                "scan_iterations":continuation.get("scan_iterations", []),
                "scan_terminal_state":continuation.get("terminal_state"),
                "scan_terminal_reason":continuation.get("terminal_reason"),
                "scan_route_selected":continuation.get("route_selected"),
                "metadata":{"source":"live_monitor_scan","priority":"high"},
            })
            data=PipelineOrchestrator().execute(intent).to_dict()
            self.write_connected_artifacts(payload, data)
            self.write_acquisition_artifacts(payload, data)
            RunHistory().rescan_exports("exports")
            compact=self.compact(data)
            compact["scan_terminal_state"]=continuation.get("terminal_state")
            compact["scan_terminal_reason"]=continuation.get("terminal_reason")
            compact["scan_iterations"]=continuation.get("scan_iterations", [])
            compact["core_output"]=data.get("core_output", {})
            return compact
        except Exception as e:
            return {"status":"failed","error":str(e),"traceback":traceback.format_exc(),"scan_iterations":continuation.get("scan_iterations", [])}
    def scan_pipeline_input(self,payload,result,continuation):
        iterations=continuation.get("scan_iterations", [])
        top_candidate=(result.get("top_candidate") or {}) if isinstance(result,dict) else {}
        solutions=((result.get("solutions") or {}).get("candidates") or []) if isinstance(result.get("solutions"),dict) else []
        gaps=result.get("gaps") or {}
        clusters=result.get("clusters") or {}
        extracted=result.get("extracted") or {}
        terminal=continuation.get("terminal_state") or "max_iterations_reached"
        reason=continuation.get("terminal_reason") or "Scan finished without a stronger terminal reason."
        missing=[]
        if not extracted.get("signal_count"): missing.append("source signal coverage")
        if not clusters.get("cluster_count"): missing.append("trend clusters")
        if not gaps.get("gap_count"): missing.append("gap evidence")
        if not solutions: missing.append("solution or portfolio candidates")
        lines=[
            "Claire live scan continuation result.",
            f"Terminal state: {terminal}.",
            f"Terminal reason: {reason}",
            f"Route selected: {continuation.get('route_selected') or 'trend_thesis'}",
            f"Market universe: {payload.get('market_universe','custom_universe')}.",
            f"Objective: {payload.get('objective','discover_market_gaps')}.",
            f"Scan iterations: {len(iterations)}.",
            f"Signals found: {extracted.get('signal_count',0)}.",
            f"Trend clusters: {clusters.get('cluster_count',0)}.",
            f"Gaps found: {gaps.get('gap_count',0)}.",
            f"Solution candidates: {len(solutions)}.",
        ]
        if top_candidate:
            lines.extend([
                f"Top candidate: {top_candidate.get('title','unnamed opportunity')}.",
                f"Top candidate market gap: {top_candidate.get('market_gap','not reported')}.",
                f"Top candidate score: {top_candidate.get('solution_score','not scored')}.",
            ])
        if missing:
            lines.append("Missing or weak selections: "+", ".join(missing)+".")
        if terminal in {"insufficient_data","max_iterations_reached"}:
            lines.append("Next recommended action: enrich sources, broaden the market universe, and rerun scan continuation before claiming breakthrough.")
        elif terminal == "breakthrough_reached":
            lines.append("Next recommended action: classify breakthrough type and select advancement path; do not default to invention unless justified.")
        else:
            lines.append("Next recommended action: review trend/thesis and portfolio action before deciding whether escalation is warranted.")
        return "\n".join(lines)
    def activate_live_candidates(self,payload):
        latest=LIVE_HISTORY.latest()
        result=payload.get("monitor_result") or latest.get("result") or {}
        if not result:
            return {"status":"not_found","activated_candidates":[]}
        bridge=MONITOR_CANDIDATE_BRIDGE.build_candidates(result,context=payload)
        public_cards=[]
        for candidate in bridge.get("candidates", [])[: int(payload.get("limit",5) or 5)]:
            candidate_id=OPPORTUNITY_CANDIDATES.put(candidate)
            stored=OPPORTUNITY_CANDIDATES.get(candidate_id) or {}
            public_cards.append(OPPORTUNITY_CANDIDATES.public_card(stored))
        return {
            "status":"success",
            "candidate_count":len(public_cards),
            "candidates":public_cards,
            "source_monitor_run_id":latest.get("monitor_run_id"),
        }
    def feed_activation_check(self,payload):
        decision=FEED_POLICY.evaluate(payload)
        audit=FEED_AUDIT.log("feed_activation_check",decision,payload)
        return {"status":"success","activation_decision":decision,"audit_event":audit}
    def scan_feed(self,payload):
        mode_decision=MODE_SWITCH.evaluate(payload)
        MODE_STATE.record("feed_scan",mode_decision,{"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision,"activation_decision":mode_decision.get("feed_activation")}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        activation=mode_decision.get("feed_activation") or FEED_POLICY.evaluate(payload)
        FEED_AUDIT.log("feed_scan_activation",activation,payload)
        if activation.get("decision")=="block":
            return {"status":"blocked","activation_decision":activation}
        if not activation.get("connected_ingestion_allowed"):
            result=FEEDS.scan(
                market_universe=payload.get("market_universe","custom_universe"),
                mode="deterministic",
                filters=payload,
            )
            result["activation_decision"]=activation
            result["mode_decision"]=mode_decision
            result["connected_ingestion_performed"]=False
            return result
        scan_payload=dict(payload)
        scan_payload["_connected_ingestion_allowed"]=True
        scan_payload["_activation_decision"]=activation
        result=FEEDS.scan(
            market_universe=payload.get("market_universe","custom_universe"),
            mode=payload.get("execution_mode","deterministic"),
            filters=scan_payload,
        )
        result["activation_decision"]=activation
        result["mode_decision"]=mode_decision
        result["connected_ingestion_performed"]=result.get("status")=="success" and bool(result.get("signals"))
        result["note"]="Public-company live scan v1 is metadata-only and environment-gated."
        return result
    def search_needed_solutions(self,payload):
        return SUGGESTIONS.suggest(
            market_universe=payload.get("market_universe","custom_universe"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            workflow=payload.get("workflow","discover"),
            signal=payload.get("signal",""),
            count=int(payload.get("count",10) or 10),
        )
    def generate_public_opportunities(self,payload):
        mode_decision=MODE_SWITCH.evaluate(payload)
        MODE_STATE.record("opportunity_generation",mode_decision,{"workflow":payload.get("workflow"),"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        generated = SEEDS.generate(
            workflow=payload.get("workflow","discover"),
            execution_mode=payload.get("execution_mode","deterministic"),
            market_universe=payload.get("market_universe","custom_universe"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            command_id=payload.get("command_id","discover_market_gaps"),
            signal=payload.get("signal",""),
            count=int(payload.get("count",5) or 5),
        )
        normalized_signals = SIGNAL_REGISTRY.list(limit=100).get("signals", [])
        public_cards=[]
        for candidate in generated.get("candidates", []):
            candidate = ENRICHER.enrich_candidate(candidate, normalized_signals, payload)
            candidate = HYBRID_FUSION.fuse_candidate(candidate, payload)
            candidate_id=OPPORTUNITY_CANDIDATES.put(candidate)
            stored=OPPORTUNITY_CANDIDATES.get(candidate_id) or {}
            public_cards.append(OPPORTUNITY_CANDIDATES.public_card(stored))
        return {
            "status":"success",
            "candidate_count":len(public_cards),
            "candidates":public_cards,
            "connected_enrichment": {
                "status": "available" if normalized_signals else "no_normalized_signals",
                "normalized_signal_count": len(normalized_signals),
                "enriched_candidate_count": len([c for c in public_cards if (c.get("connected_enrichment") or {}).get("safe_to_enrich")]),
            },
            "hybrid_fusion": {
                "status": "available",
                "hybrid_candidate_count": len([c for c in public_cards if (c.get("hybrid_fusion") or {}).get("status") == "hybrid_ready"]),
                "recommended_hybrid_count": len([c for c in public_cards if (c.get("hybrid_fusion") or {}).get("recommended_mode") in {"hybrid", "hybrid_candidate"}]),
            },
            "workflow":generated.get("workflow"),
            "execution_mode":generated.get("execution_mode"),
            "market_universe":generated.get("market_universe"),
            "industry_domain":generated.get("industry_domain"),
            "buyer_segment":generated.get("buyer_segment"),
            "objective":generated.get("objective"),
            "mode_decision":mode_decision,
        }
    def enrichment_status(self):
        signals = SIGNAL_REGISTRY.list(limit=100).get("signals", [])
        return {
            "status":"success",
            "enricher":"connected_opportunity_enricher_v1",
            "normalized_signal_count":len(signals),
            "safe_to_enrich_count":len([s for s in signals if s.get("safe_to_enrich")]),
            "supported_outputs":["public_opportunity_card","protected_launch_prompt"],
        }
    def fusion_status(self):
        signals = SIGNAL_REGISTRY.list(limit=100).get("signals", [])
        return {
            "status":"success",
            "fusion_engine":"hybrid_opportunity_fusion_v1",
            "normalized_signal_count":len(signals),
            "purpose":"Fuse deterministic opportunity selection with safe connected enrichment.",
            "supported_outputs":["hybrid_readiness","recommended_mode","fusion_summary","protected_launch_prompt"],
        }
    def enrich_preview(self,payload):
        generated = SEEDS.generate(
            workflow=payload.get("workflow","discover"),
            execution_mode=payload.get("execution_mode","deterministic"),
            market_universe=payload.get("market_universe","custom_universe"),
            industry_domain=payload.get("industry_domain","cross_sector"),
            buyer_segment=payload.get("buyer_segment","enterprise_c_suite"),
            objective=payload.get("objective","discover_market_gaps"),
            command_id=payload.get("command_id","discover_market_gaps"),
            signal=payload.get("signal",""),
            count=1,
        )
        candidate = (generated.get("candidates") or [{}])[0]
        signals = payload.get("normalized_signals") or SIGNAL_REGISTRY.list(limit=100).get("signals", [])
        enriched = ENRICHER.enrich_candidate(candidate, signals, payload)
        enriched = HYBRID_FUSION.fuse_candidate(enriched, payload)
        public = OPPORTUNITY_CANDIDATES.public_card(enriched)
        return {"status":"success","candidate":public,"connected_enrichment":public.get("connected_enrichment",{})}
    def fusion_preview(self,payload):
        preview = self.enrich_preview(payload)
        return {
            "status":"success",
            "candidate":preview.get("candidate"),
            "hybrid_fusion":(preview.get("candidate") or {}).get("hybrid_fusion",{}),
        }
    def run_candidate(self,payload):
        candidate_id=payload.get("candidate_id")
        candidate=OPPORTUNITY_CANDIDATES.get(candidate_id or "")
        if not candidate: return {"status":"not_found","error":"candidate not found or expired"}
        launch_payload={
            "raw_input":candidate.get("raw_input",""),
            "workflow":candidate.get("workflow"),
            "execution_mode":candidate.get("execution_mode"),
            "market_universe":candidate.get("market_universe"),
            "industry_domain":candidate.get("industry_domain"),
            "buyer_segment":candidate.get("buyer_segment"),
            "objective":candidate.get("objective"),
            "connected_enrichment":candidate.get("connected_enrichment"),
            "hybrid_fusion":candidate.get("hybrid_fusion"),
        }
        return self.eval_async(launch_payload)
    def events(self,path,query):
        parts=[unquote(p) for p in path.split("/") if p]
        since=query.get("since",[None])[0]
        since=int(since) if since is not None and str(since).isdigit() else None
        return self.json(RUN_EVENTS.get(parts[2],since))
    def eval_async(self,payload):
        raw=(payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw: return {"status":"validation_failed","error":"raw_input is required"}
        mode_decision=MODE_SWITCH.evaluate({**payload,"raw_input":raw})
        MODE_STATE.record("dashboard_launch",mode_decision,{"workflow":payload.get("workflow"),"market_universe":payload.get("market_universe")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision,"decision":mode_decision.get("governance_decision")}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        metadata={
            "source":"dashboard",
            "workflow":payload.get("workflow"),
            "market_universe":payload.get("market_universe"),
            "industry_domain":payload.get("industry_domain"),
            "buyer_segment":payload.get("buyer_segment"),
            "objective":payload.get("objective"),
            "execution_mode":payload.get("execution_mode"),
            "mode_decision":mode_decision,
            "connected_enrichment":payload.get("connected_enrichment"),
            "hybrid_fusion":payload.get("hybrid_fusion"),
        }
        governance_decision=GOVERNANCE.classify(raw,metadata)
        LEGAL_AUDIT.log("dashboard_launch_precheck",governance_decision,metadata)
        if governance_decision.get("decision")=="block":
            return {"status":"blocked","decision":governance_decision}
        feed_activation=mode_decision.get("feed_activation") or FEED_POLICY.evaluate(payload)
        FEED_AUDIT.log("dashboard_launch_feed_activation",feed_activation,payload)
        run_id=RUN_EVENTS.create_run(raw[:80]+("..." if len(raw)>80 else ""),metadata)
        RUN_EVENTS.add(run_id,"stage_complete","Governance precheck: "+governance_decision.get("decision","allow"),"governance",4,governance_decision)
        RUN_EVENTS.add(run_id,"stage_complete",f"Mode decision: {mode_decision.get('requested_mode')} -> {mode_decision.get('effective_mode')}.","mode",5,mode_decision)
        threading.Thread(target=self.worker,args=(run_id,raw,payload),daemon=True).start()
        RUN_EVENTS.add(run_id,"started","Background Claire evaluation started.","launcher",3)
        return {"status":"started","event_run_id":run_id}
    def worker(self,run_id,raw,payload):
        try:
            RUN_EVENTS.add(run_id,"stage_started","Validating request.","contract",6)
            mode=self.normalize_mode(payload.get("execution_mode"))
            intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow"),"market_universe":payload.get("market_universe"),"industry_domain":payload.get("industry_domain"),"buyer_segment":payload.get("buyer_segment"),"objective":payload.get("objective")}})
            RUN_EVENTS.add(run_id,"stage_complete",f"Contract validation complete. Execution mode: {mode}.","contract",10)
            RUN_EVENTS.add(run_id,"stage_started","Running Claire pipeline.","pipeline",15)
            result=PipelineOrchestrator().execute(intent)
            data=result.to_dict() if hasattr(result,"to_dict") else result
            RUN_EVENTS.add(run_id,"stage_complete","Core pipeline complete.","pipeline",70)
            summary=data.get("lifecycle_summary") or {}
            if summary: RUN_EVENTS.add(run_id,"stage_complete",f"Lifecycle: {summary.get('active_stage_count')}/{summary.get('implemented_stage_count')} active.","lifecycle",80,summary)
            ew=data.get("export_writer") or {}
            if ew: RUN_EVENTS.add(run_id,"stage_complete",f"Export writer: {ew.get('status')}","export_writer",88,{"output_dir":ew.get("output_dir")})
            connected_artifacts = self.write_connected_artifacts(payload, data)
            if connected_artifacts.get("status")=="success":
                RUN_EVENTS.add(run_id,"stage_complete",f"Connected/hybrid artifacts: {connected_artifacts.get('written_file_count')} file(s).","connected_exports",92,connected_artifacts)
            acquisition_artifacts = self.write_acquisition_artifacts(payload, data)
            if acquisition_artifacts.get("status")=="success":
                RUN_EVENTS.add(run_id,"stage_complete",f"Acquisition artifacts: {acquisition_artifacts.get('written_file_count')} file(s).","acquisition_exports",94,acquisition_artifacts)
            RunHistory().rescan_exports("exports")
            compact=self.compact(data)
            compact["connected_export_artifacts"] = connected_artifacts
            compact["acquisition_export_artifacts"] = acquisition_artifacts
            RUN_EVENTS.set_result(run_id,compact)
            RUN_EVENTS.add(run_id,"complete","Claire run complete. Export artifacts are ready.","complete",100,compact)
        except Exception as e:
            RUN_EVENTS.add(run_id,"error",str(e),"error",100,{"traceback":traceback.format_exc()},"error")
    def eval_sync(self,payload):
        raw=(payload.get("raw_input") or payload.get("text") or "").strip()
        if not raw: return {"status":"validation_failed","error":"raw_input is required"}
        mode_decision=MODE_SWITCH.evaluate({**payload,"raw_input":raw})
        MODE_STATE.record("dashboard_sync_launch",mode_decision,{"workflow":payload.get("workflow")})
        if mode_decision.get("status")=="blocked":
            return {"status":"blocked","mode_decision":mode_decision}
        payload=MODE_ISOLATION.isolate(payload,mode_decision)
        mode=self.normalize_mode(payload.get("execution_mode"))
        intent=ContractValidator().validate_intent({"raw_input":raw,"mode":mode,"metadata":{"source":"dashboard","priority":"high","workflow":payload.get("workflow")}})
        result=PipelineOrchestrator().execute(intent)
        data=result.to_dict() if hasattr(result,"to_dict") else result
        self.write_connected_artifacts(payload, data)
        self.write_acquisition_artifacts(payload, data)
        RunHistory().rescan_exports("exports")
        compact=self.compact(data)
        compact["mode_decision"]=mode_decision
        return compact
    def write_connected_artifacts(self,payload,data):
        ew=data.get("export_writer") or {}
        output_dir=ew.get("output_dir")
        signals=SIGNAL_REGISTRY.list(limit=100).get("signals", [])
        if not output_dir:
            return {"status":"skipped","reason":"export_writer output_dir unavailable"}
        return CONNECTED_EXPORTS.write(
            output_dir=output_dir,
            payload=payload,
            normalized_signals=signals,
            run_result=data,
        )
    def write_acquisition_artifacts(self,payload,data):
        ew=data.get("export_writer") or {}
        output_dir=ew.get("output_dir")
        if not output_dir:
            return {"status":"skipped","reason":"export_writer output_dir unavailable"}
        return ACQUISITION_EXPORTS.write(output_dir=output_dir,run_result=data,payload=payload)
    def normalize_mode(self, mode):
        return MODE_SWITCH.normalize(mode)
    def compact(self,data):
        ew=data.get("export_writer") or {}; hr=ew.get("history_record") or {}; ep=data.get("export_package") or {}
        core=data.get("core_output") or {}; u=core.get("user_facing_result") or {}
        return {"status":data.get("status","success"),"run_id":hr.get("run_id") or ew.get("folder_name"),"folder_name":ew.get("folder_name"),"route_selected":core.get("route_selected"),"headline":u.get("headline"),"summary":u.get("summary"),"confidence":(core.get("confidence") or {}).get("overall"),"decision_classification":data.get("decision_classification"),"breakthrough_classification":data.get("breakthrough_classification"),"export_level":(ep.get("export_package_score") or {}).get("level"),"export_writer":{"status":ew.get("status"),"output_dir":ew.get("output_dir"),"folder_name":ew.get("folder_name"),"written_file_count":ew.get("written_file_count"),"history_record":hr},"lifecycle_summary":data.get("lifecycle_summary"),"scores":data.get("scores")}
    def body(self):
        n=int(self.headers.get("Content-Length","0") or 0); raw=self.rfile.read(n).decode("utf-8") if n else "{}"; return json.loads(raw or "{}")
    def run_api(self,path,query):
        parts=[unquote(p) for p in path.split("/") if p]; run_id=parts[2]; browser=ExportBrowser()
        if len(parts)==3: return self.json(browser.get_run(run_id))
        if len(parts)==4 and parts[3]=="files": return self.json(browser.list_files(run_id))
        if len(parts)==5 and parts[3]=="files":
            filename=parts[4]; raw=query.get("raw",["0"])[0]=="1"; maxc=int(query.get("max_chars",["0"])[0] or 0); res=browser.read_file(run_id,filename,max_chars=maxc or None)
            if raw and res.get("status")=="success": return self.text(res.get("content",""),filename)
            return self.json(res)
        self.send_error(404,"Unsupported run API path")
    def file(self,path):
        if not path.exists() or not path.is_file(): return self.send_error(404,f"File not found: {path.name}")
        data=path.read_bytes(); mime,_=mimetypes.guess_type(str(path)); self.send_response(200); self.send_header("Content-Type",mime or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def json(self,payload,status=200):
        data=json.dumps(payload,indent=2,default=str).encode("utf-8"); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
    def text(self,content,filename="artifact.txt"):
        suf=Path(filename).suffix.lower(); mime="application/json" if suf==".json" else "text/markdown" if suf==".md" else "text/plain"; data=content.encode("utf-8"); self.send_response(200); self.send_header("Content-Type",f"{mime}; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--host",default="127.0.0.1"); ap.add_argument("--port",type=int,default=8765); ap.add_argument("--no-open",action="store_true"); args=ap.parse_args()
    if not (DASHBOARD_DIR/"index.html").exists(): raise SystemExit(f"Dashboard files not found at {DASHBOARD_DIR}")
    srv=ThreadingHTTPServer((args.host,args.port),Handler); url=f"http://{args.host}:{args.port}"; print(f"Claire Dashboard running at {url}"); print("Press Ctrl+C to stop.")
    if not args.no_open: webbrowser.open(url)
    try: srv.serve_forever()
    except KeyboardInterrupt: print("\\nStopping dashboard.")
    finally: srv.server_close()
if __name__=="__main__": main()
