from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Any


VERSION = "v19.89.8_pipeline_activation_registry"


PIPELINES: list[dict[str, Any]] = [
    {"id": "knowledge_ingestion", "label": "Knowledge Ingestion", "module": "runtime_core.engines.knowledge_ingestion_engine", "class": "KnowledgeIngestionEngine"},
    {"id": "signal_extraction", "label": "Signal Extraction", "module": "runtime_core.engines.signal_extraction_engine", "class": "SignalExtractionEngine"},
    {"id": "market_formation", "label": "Market Formation", "module": "runtime_core.engines.market_formation_engine", "class": "MarketFormationEngine"},
    {"id": "market_gap", "label": "Market Gap", "module": "runtime_core.engines.market_gap_engine", "class": "MarketGapEngine"},
    {"id": "breakthrough_synthesis", "label": "Breakthrough Synthesis", "module": "runtime_core.engines.breakthrough_synthesis_engine", "class": "BreakthroughSynthesisEngine"},
    {"id": "technology_intelligence", "label": "Technology Intelligence", "module": "runtime_core.technology.technology_intelligence", "class": "TechnologyIntelligenceLayer"},
    {"id": "technical_feasibility", "label": "Technical Feasibility", "module": "runtime_core.engines.technical_feasibility_engine", "class": "TechnicalFeasibilityEngine"},
    {"id": "system_design", "label": "System Design", "module": "runtime_core.engines.system_design_engine", "class": "SystemDesignEngine"},
    {"id": "auto_design", "label": "Auto Design", "module": "runtime_core.engines.auto_design", "class": "AutoDesignEngine"},
    {"id": "portfolio_optimization", "label": "Portfolio Optimization", "module": "runtime_core.portfolio.optimization_engine", "class": "PortfolioOptimizationEngine"},
    {"id": "acquirer_matching", "label": "Acquirer Matching", "module": "runtime_core.engines.acquirer_matching", "class": "AcquirerMatchingEngine"},
    {"id": "productization_path", "label": "Productization Path", "module": "runtime_core.engines.productization_path_engine", "class": "ProductizationPathEngine"},
    {"id": "deal_exit_modeling", "label": "Deal Exit Modeling", "module": "runtime_core.engines.deal_exit_modeling_engine", "class": "DealExitModelingEngine"},
    {"id": "export_package", "label": "Export Package", "module": "runtime_core.engines.export_package_engine", "class": "ExportPackageEngine"},
]

PIPELINE_TRIGGER_SCORE_ROUTE: dict[str, dict[str, Any]] = {
    "knowledge_ingestion": {
        "what": "Normalize source records into governed knowledge inputs",
        "why": "Every downstream score depends on traceable source intake",
        "when": "operator submits a query, file intake, or governed source packet",
        "trigger": "source_packet_received",
        "score": ["source_trust", "ingestion_completeness", "traceability"],
        "route": "portfolio",
        "sequence": [1, 2, 3],
        "output": "normalized source packet",
        "failure_state": "untrusted_or_incomplete_source_packet",
    },
    "signal_extraction": {
        "what": "Extract weak signals and entities from governed inputs",
        "why": "Route selection starts with signal family and evidence quality",
        "when": "normalized source packet is available",
        "trigger": "normalized_source_packet",
        "score": ["signal_strength", "source_trust", "entity_confidence"],
        "route": "portfolio",
        "sequence": [4, 5, 6, 7],
        "output": "ranked signal set",
        "failure_state": "signal_below_threshold",
    },
    "market_formation": {
        "what": "Detect market formation pressure",
        "why": "Portfolio routing needs market context before escalation",
        "when": "clustered trend evidence exists",
        "trigger": "trend_cluster_detected",
        "score": ["market_pressure", "adoption_velocity", "category_clarity"],
        "route": "portfolio",
        "sequence": [8, 9, 10],
        "output": "market formation thesis",
        "failure_state": "market_context_too_weak",
    },
    "market_gap": {
        "what": "Qualify gaps and unmet demand",
        "why": "Breakthrough and portfolio routes diverge at gap severity",
        "when": "market formation thesis is present",
        "trigger": "qualified_market_thesis",
        "score": ["gap_validity", "gap_severity", "portfolio_relevance"],
        "route": "breakthrough",
        "sequence": [11, 12],
        "output": "qualified gap contract",
        "failure_state": "gap_not_actionable",
    },
    "breakthrough_synthesis": {
        "what": "Classify whether the gap exceeds normal portfolio handling",
        "why": "Center selection depends on breakthrough threshold and family",
        "when": "gap severity and discovery quality pass",
        "trigger": "qualified_gap_contract",
        "score": ["breakthrough_threshold", "novelty", "advancement_path_confidence"],
        "route": "breakthrough",
        "sequence": [13, 14, 15],
        "output": "breakthrough classification",
        "failure_state": "portfolio_only_signal",
    },
    "technology_intelligence": {
        "what": "Assess technology lineage, feasibility signals, and buildability",
        "why": "Tech design/build requires construction-ready evidence",
        "when": "breakthrough primary family is technical or buildable-now",
        "trigger": "technical_breakthrough_classification",
        "score": ["technology_signal", "readiness_level", "dependency_confidence"],
        "route": "tech_design_build",
        "sequence": [15, 16, 17],
        "output": "technology intelligence contract",
        "failure_state": "technical_evidence_insufficient",
    },
    "technical_feasibility": {
        "what": "Prove buildability, viability, manufacturability, and deployability",
        "why": "Design portal must not advance without feasibility gates",
        "when": "technology intelligence is ready",
        "trigger": "technology_intelligence_contract",
        "score": ["buildability_readiness", "viability", "manufacturability"],
        "route": "tech_design_build",
        "sequence": [18, 19, 20, 21],
        "output": "technical feasibility proof",
        "failure_state": "design_route_blocked",
    },
    "system_design": {
        "what": "Generate architecture and implementation plan",
        "why": "Design portal output needs backend-owned structure",
        "when": "technical feasibility passes",
        "trigger": "technical_feasibility_proof",
        "score": ["design_route_readiness", "dependency_risk", "implementation_confidence"],
        "route": "tech_design_build",
        "sequence": [21, 22],
        "output": "design portal contract",
        "failure_state": "blueprint_not_ready",
    },
    "auto_design": {
        "what": "Create governed autodesign handoff",
        "why": "CAD intent is downstream of design portal, not a direct route",
        "when": "design portal contract is ready",
        "trigger": "design_portal_contract",
        "score": ["handoff_completeness", "cad_intent_readiness", "traceability"],
        "route": "tech_design_build",
        "sequence": [22],
        "output": "autodesign handoff and CAD intent",
        "failure_state": "cad_intent_unavailable",
    },
    "portfolio_optimization": {
        "what": "Turn thesis and evidence into portfolio action",
        "why": "Portfolio is the default path for market-strength signals",
        "when": "portfolio relevance passes and no higher route owns it",
        "trigger": "portfolio_signal_family",
        "score": ["trend_strength", "thesis_quality", "portfolio_relevance", "risk_exposure"],
        "route": "portfolio",
        "sequence": [23, 26, 27],
        "output": "portfolio artifact",
        "failure_state": "generic_portfolio_output",
    },
    "acquirer_matching": {
        "what": "Find strategic buyers and acquisition fit",
        "why": "Acquisition route requires buyer-specific rationale",
        "when": "moat, value capture, and acquirer fit pass",
        "trigger": "acquisition_signal_family",
        "score": ["moat", "value_capture", "acquirer_fit"],
        "route": "acquisition",
        "sequence": [28, 29],
        "output": "acquirer match set",
        "failure_state": "no_buyer_fit",
    },
    "productization_path": {
        "what": "Select productization or packaging path",
        "why": "Output must match the selected route rather than a generic artifact",
        "when": "portfolio, design, or acquisition output is ready",
        "trigger": "route_output_ready",
        "score": ["productization_fit", "delivery_confidence", "operator_value"],
        "route": "portfolio",
        "sequence": [27, 30],
        "output": "productization path",
        "failure_state": "unclear_productization_path",
    },
    "deal_exit_modeling": {
        "what": "Model deal logic and exit rationale",
        "why": "Acquisition packages need value capture and exit proof",
        "when": "acquirer match set exists",
        "trigger": "acquirer_match_set",
        "score": ["deal_fit", "exit_value", "strategic_urgency"],
        "route": "acquisition",
        "sequence": [29, 30],
        "output": "deal exit model",
        "failure_state": "deal_logic_unproven",
    },
    "export_package": {
        "what": "Construct final governed package",
        "why": "The operator needs a traceable artifact at the end of the route",
        "when": "selected route output passes quality gate",
        "trigger": "route_quality_gate_passed",
        "score": ["output_quality", "traceability", "replayability"],
        "route": "recursive_memory",
        "sequence": [30, "memory", "replay"],
        "output": "final package and recursive memory candidate",
        "failure_state": "package_blocked_until_traceable",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inspect_pipeline(definition: dict[str, Any]) -> dict[str, Any]:
    contract = PIPELINE_TRIGGER_SCORE_ROUTE.get(definition["id"], {})
    try:
        module = importlib.import_module(definition["module"])
    except Exception as exc:
        return {
            **definition,
            **contract,
            "owner_file": definition["module"],
            "trigger_score_route": contract,
            "status": "missing_or_import_failed",
            "error": f"{type(exc).__name__}: {exc}",
            "dashboard_bound": False,
        }
    cls = getattr(module, definition["class"], None)
    if cls is None:
        return {
            **definition,
            **contract,
            "owner_file": definition["module"],
            "trigger_score_route": contract,
            "status": "missing_class",
            "dashboard_bound": False,
        }
    structural_placeholder = bool(getattr(cls, "structural_placeholder", False))
    implemented = not structural_placeholder
    activation_methods = ("analyze", "execute", "run", "generate", "optimize", "match", "build")
    methods = [name for name in activation_methods if callable(getattr(cls, name, None))]
    if structural_placeholder:
        status = "placeholder"
    elif methods:
        status = "activated"
    else:
        status = "present_unbound"
    return {
        **definition,
        **contract,
        "owner_file": definition["module"],
        "trigger_score_route": contract,
        "status": status,
        "implemented": implemented,
        "structural_placeholder": structural_placeholder,
        "methods": methods,
        "dashboard_bound": definition["id"] in {
            "technology_intelligence",
            "knowledge_ingestion",
            "signal_extraction",
            "system_design",
            "auto_design",
            "portfolio_optimization",
            "acquirer_matching",
            "export_package",
        },
    }


def select_pipeline_route(scores: dict[str, Any] | None = None, trigger: str | None = None) -> dict[str, Any]:
    scores = scores or {}
    trigger_value = str(trigger or scores.get("trigger") or "").strip()
    route = str(scores.get("route") or "").strip()
    if not route:
        if float(scores.get("acquirer_fit", 0) or 0) >= 0.5 and float(scores.get("moat", 0) or 0) >= 0.5:
            route = "acquisition"
        elif float(scores.get("technology_signal", 0) or 0) >= 0.55 and float(scores.get("buildability_readiness", 0) or 0) >= 0.5:
            route = "tech_design_build"
        elif float(scores.get("breakthrough_threshold", 0) or 0) >= 0.6 and "gap" in trigger_value:
            route = "breakthrough"
        elif bool(scores.get("operator_approved")) and float(scores.get("traceability", 0) or 0) >= 0.75:
            route = "recursive_memory"
        else:
            route = "portfolio"
    pipelines = [
        pipeline_id
        for pipeline_id, contract in PIPELINE_TRIGGER_SCORE_ROUTE.items()
        if contract.get("route") == route
    ]
    return {
        "schema_version": "claire.acs2.trigger_score_route.selector.v1",
        "status": "ready",
        "selected_route": route,
        "pipeline_ids": pipelines,
        "trigger": trigger_value,
        "score_keys": sorted(scores),
        "authority": {
            "runtime_truth_mutation": False,
            "dashboard_may_render_only": True,
        },
    }


def build_pipeline_activation_registry() -> dict[str, Any]:
    items = [inspect_pipeline(item) for item in PIPELINES]
    activated = [item for item in items if item["status"] == "activated"]
    placeholders = [item for item in items if item["status"] == "placeholder"]
    unbound = [item for item in items if item["status"] == "present_unbound"]
    failed = [item for item in items if item["status"] in {"missing_or_import_failed", "missing_class"}]
    return {
        "schema_version": VERSION,
        "status": "ready",
        "generated_at": utc_now(),
        "pipeline_count": len(items),
        "activated_count": len(activated),
        "placeholder_count": len(placeholders),
        "unbound_count": len(unbound),
        "failed_count": len(failed),
        "dashboard_bound_count": len([item for item in items if item.get("dashboard_bound")]),
        "decision_layer": "ACS2 trigger-score-route execution map",
        "route_execution_map": {
            item["id"]: item.get("trigger_score_route", {})
            for item in items
        },
        "representative_route_selection": {
            "portfolio": select_pipeline_route({"trend_strength": 0.62, "portfolio_relevance": 0.71}, "portfolio_signal_family"),
            "tech_design_build": select_pipeline_route({"technology_signal": 0.7, "buildability_readiness": 0.66}, "technical_breakthrough_classification"),
            "acquisition": select_pipeline_route({"moat": 0.74, "acquirer_fit": 0.7}, "acquisition_signal_family"),
        },
        "items": items,
        "next_activation_order": [
            item["id"]
            for item in items
            if item["status"] in {"placeholder", "present_unbound", "missing_or_import_failed", "missing_class"}
        ][:10],
        "authority": {
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutation": False,
            "automatic_update_performed": False,
        },
    }
