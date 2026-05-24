"""Compatibility bridge for the enhanced Claire-Syntalion interface concept."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class EnhancedCapability:
    capability_id: str
    label: str
    section: str
    upload_function: str
    backend_endpoint: str
    service_package: str
    state: str
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EnhancedInterfaceBridge:
    """Map the uploaded enhanced dashboard concept to installed Claire services."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def capabilities(self) -> List[EnhancedCapability]:
        return [
            EnhancedCapability("claire_search", "CLAIRE Search", "global", "handleSearch", "/api/enhanced-interface/action", "command_catalog_and_opportunity_search", "ready", "Routes search intent into needed-solution and opportunity discovery services."),
            EnhancedCapability("mode_switching", "Mode Switching", "global", "switchMode", "/api/modes/evaluate", "mode_governance", "ready", "Deterministic, connected, and hybrid modes are governed and auditable."),
            EnhancedCapability("launch_process", "Launch Process", "global", "launchProcess", "/api/evaluate/async", "dashboard_run_launcher", "ready", "Launches the protected Claire pipeline with live run events."),
            EnhancedCapability("live_discoveries", "Live Discoveries", "discovery", "openDiscovery", "/api/feeds/live-orchestration/run", "live_source_orchestration", "ready", "Prepares live intelligence from governed source catalogs."),
            EnhancedCapability("market_analysis", "Market Analysis", "discovery", "openMarketAnalysis", "/api/opportunities/generate", "market_universe_taxonomy", "ready", "Uses market universe, domain, buyer, and objective selectors to generate opportunity candidates."),
            EnhancedCapability("innovation_search", "Innovation Search", "discovery", "openInnovationSearch", "/api/opportunities/search-needed-solutions", "opportunity_command_library", "ready", "Searches needed-solution directions across the active opportunity context."),
            EnhancedCapability("financial_markets", "Financial Markets", "data_sources", "openFinancialMarkets", "/api/feeds/live-source-catalog/resolve", "public_company_live_source_catalog", "starter_ready", "Public-company market source packs are installed; full market-data APIs remain future connectors."),
            EnhancedCapability("news_intelligence", "News Intelligence", "data_sources", "openNewsIntelligence", "/api/feeds/live-source-catalog/resolve", "public_market_news_metadata_pack", "starter_ready", "Public news landing pages are available for metadata-only signals; article-body ingestion is intentionally not enabled."),
            EnhancedCapability("patent_database", "Patent Database", "data_sources", "openPatentDatabase", "/api/live-intelligence/connectors/run", "uspto_patent_metadata_connector", "starter_ready", "USPTO public patent metadata connector is installed for governed innovation and defensibility signals."),
            EnhancedCapability("company_intel", "Company Intel", "data_sources", "openCompanyIntel", "/api/feeds/public-company-live/scan", "public_company_live_scan", "ready", "Investor-relations and public-reference source packs feed company metadata signals."),
            EnhancedCapability("analysis_customization", "Analysis Customization", "customization", "openCustomization('analysis')", "/api/lifecycle/threshold-provenance", "threshold_provenance", "ready", "Lifecycle thresholds and calibration inputs are visible and test-covered."),
            EnhancedCapability("trends_customization", "Trends Customization", "customization", "openCustomization('trends')", "/api/lifecycle/stage-registry", "stage_registry", "ready", "Trend trajectory is represented in the lifecycle spine and stage registry."),
            EnhancedCapability("discovery_customization", "Discovery Customization", "customization", "openCustomization('discovery')", "/api/commands", "opportunity_command_catalog", "ready", "Discovery commands, universes, domains, buyers, and objectives are catalog-driven."),
            EnhancedCapability("breakthrough_customization", "Breakthrough Customization", "customization", "openCustomization('breakthrough')", "/api/lifecycle/threshold-provenance", "breakthrough_thresholds", "ready", "Breakthrough rules are captured in threshold provenance."),
            EnhancedCapability("innovation_customization", "Innovation Customization", "customization", "openCustomization('innovation')", "/api/opportunities/generate", "opportunity_generation", "ready", "Innovation candidates are generated through protected opportunity cards."),
            EnhancedCapability("portfolio_customization", "Portfolio Customization", "customization", "openCustomization('portfolio')", "/api/exports/acquisition-preview", "acquisition_export_upgrade", "ready", "Portfolio, acquirer, value-capture, and diligence sections are present."),
            EnhancedCapability("active_portfolios", "Active Portfolios", "portfolio", "openActivePortfolios", "/api/runs", "export_browser_and_run_history", "ready", "Completed runs and export artifacts provide local portfolio history."),
            EnhancedCapability("buyer_matching", "Buyer Matching", "portfolio", "openBuyerMatching", "/api/exports/acquisition-preview", "acquirer_discovery", "ready", "Acquirer discovery preview is wired into acquisition export artifacts."),
            EnhancedCapability("deal_pipeline", "Deal Pipeline", "portfolio", "openDealPipeline", "/api/exports/acquisition-preview", "deal_exit_modeling", "ready", "Deal/exit modeling appears in the lifecycle and acquisition preview stack."),
            EnhancedCapability("system_configuration", "System Configuration", "settings", "openSettings", "/api/portable/status", "portable_desktop_readiness", "ready", "Portable path validation and launcher readiness are available."),
            EnhancedCapability("security", "Security", "settings", "openSettings", "/api/governance/audit", "governance_and_redline_audit", "ready", "Governance, legal audit, source allowlists, updater verification, and rollback controls are installed."),
            EnhancedCapability("audit", "Audit", "settings", "openSettings", "/api/feeds/audit", "legal_and_feed_audit_logs", "ready", "Feed and governance audit logs are dashboard-visible."),
            EnhancedCapability("engine_management", "Engine Management", "settings", "openSettings", "/api/services/status", "desktop_service_status", "ready", "Desktop service status reports launcher, feeds, updater, export browser, and runtime readiness."),
        ]

    def status(self) -> Dict[str, Any]:
        capabilities = [capability.to_dict() for capability in self.capabilities()]
        ready = [item for item in capabilities if item["state"] in {"ready", "starter_ready"}]
        planned = [item for item in capabilities if item["state"] == "planned"]
        return {
            "status": "success",
            "bridge_version": "v5.71",
            "source_upload": "claire-syntalion-enhanced.html",
            "capability_count": len(capabilities),
            "ready_or_starter_count": len(ready),
            "planned_count": len(planned),
            "readiness": "upload_functional_with_starter_connectors" if not planned else "upload_functional_with_known_connector_gaps",
            "capabilities": capabilities,
            "known_connector_gaps": planned,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action_id = payload.get("action_id", "")
        capability = next((item for item in self.capabilities() if item.capability_id == action_id), None)
        if capability is None:
            return {
                "status": "unknown_action",
                "action_id": action_id,
                "message": "No enhanced interface capability is registered for this action.",
            }
        return {
            "status": "success",
            "action_id": action_id,
            "capability": capability.to_dict(),
            "recommended_endpoint": capability.backend_endpoint,
            "payload_passthrough": payload,
            "message": f"{capability.label} is mapped to {capability.service_package}.",
        }
