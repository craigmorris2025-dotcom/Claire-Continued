from __future__ import annotations

"""
Claire Knowledge Base Registry From Uploaded Docs — S471-S477

This module creates the first canonical, deterministic Claire knowledge-base
registry from the most important uploaded platform documents and pipeline notes.

It does not read external files at runtime. It records the current canonical
document map, route anchors, domain tags, trust tiers, and search/retrieval
contracts so Claire's Q&A layer can begin grounding answers in platform-specific
knowledge rather than generic chatbot behavior.

Builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Response Cards
- S464-S470 Evidence-Backed Answer Model

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, or autonomous execution are performed here.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S471-S477"
PHASE = "S471-S477"
JS_ASSET = "frontend/cockpit/shell/assets/claire_knowledge_base_registry.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_knowledge_base_registry.css"


BLOCKED_AUTHORITY: Dict[str, bool] = {
    "runtime_mutation_enabled": False,
    "runtime_truth_mutation_allowed": False,
    "runtime_truth_write_allowed": False,
    "automatic_updates_enabled": False,
    "autonomous_crawling_enabled": False,
    "autonomous_execution_enabled": False,
    "autonomous_agent_execution_enabled": False,
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
}


TRUST_TIERS: Dict[str, Dict[str, Any]] = {
    "governing": {
        "weight": 0.96,
        "description": "Authoritative platform definition or safety/governance source.",
    },
    "canonical": {
        "weight": 0.90,
        "description": "Canonical lifecycle, route, pipeline, or data model source.",
    },
    "architectural": {
        "weight": 0.86,
        "description": "Subsystem, execution flow, mode, or implementation architecture source.",
    },
    "technical_reference": {
        "weight": 0.82,
        "description": "Technology database, technology search, or engineering reference source.",
    },
    "legacy_context": {
        "weight": 0.68,
        "description": "Older historical context that may inform but not override current architecture.",
    },
}


DOMAIN_TAGS = [
    "identity",
    "governance",
    "safety",
    "mode_architecture",
    "deterministic_mode",
    "connected_mode",
    "hybrid_mode",
    "lifecycle",
    "route_selection",
    "signal_governance",
    "trend_discovery",
    "portfolio",
    "breakthrough",
    "acquisition",
    "engineering",
    "design_portal",
    "technology_intelligence",
    "evidence",
    "recursive_learning",
    "update_governance",
    "dashboard",
    "data_model",
    "system_transformation",
]


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    title: str
    trust_tier: str
    source_type: str
    status: str
    summary: str
    domains: List[str]
    route_anchors: List[str]
    key_claims: List[str]
    limitations: List[str]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _safe_base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "version": VERSION,
        "phase": PHASE,
        "stage_version": stage_version,
        "status": status,
        "ready": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "created_at": _now(),
    }
    payload.update(BLOCKED_AUTHORITY)
    payload.update(extra)
    return payload


def _doc(
    doc_id: str,
    title: str,
    trust_tier: str,
    source_type: str,
    status: str,
    summary: str,
    domains: Sequence[str],
    route_anchors: Sequence[str],
    key_claims: Sequence[str],
    limitations: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    return asdict(
        KnowledgeDocument(
            doc_id=doc_id,
            title=title,
            trust_tier=trust_tier,
            source_type=source_type,
            status=status,
            summary=summary,
            domains=list(domains),
            route_anchors=list(route_anchors),
            key_claims=list(key_claims),
            limitations=list(limitations or []),
        )
    )


def build_canonical_knowledge_documents() -> List[Dict[str, Any]]:
    """Return the curated knowledge document registry from uploaded Claire materials."""
    return [
        _doc(
            "claire_unified_platform_definition_v1",
            "Claire Syntalion Unified Platform Definition v1",
            "governing",
            "compiled_current_definition",
            "current",
            "Current compact platform definition consolidating Claire identity, specs, operations, functionality, governance, lifecycle, and roadmap.",
            ["identity", "lifecycle", "governance", "portfolio", "breakthrough", "acquisition", "engineering", "recursive_learning"],
            ["all_routes", "operator_reference"],
            [
                "Claire is a governed lifecycle intelligence platform.",
                "The 30-stage lifecycle is canonical.",
                "Q&A should be intelligence-routed and evidence-aware.",
            ],
        ),
        _doc(
            "claire_master_system_build_plan",
            "Claire Master System Build Plan - Singularity-Aligned Edition",
            "governing",
            "uploaded_master_document",
            "current_guiding_document",
            "Master governing document defining Claire as a recursive trend-discovery, portfolio-construction, breakthrough-escalation, system-transformation, and acquisition-readiness platform.",
            ["identity", "lifecycle", "route_selection", "portfolio", "breakthrough", "acquisition", "recursive_learning"],
            ["signal_to_portfolio", "breakthrough_escalation", "final_package", "recursive_self_ingestion"],
            [
                "Claire's root system is signal governance to trend discovery to thesis formation to portfolio creation or optimization.",
                "Breakthrough escalation is conditional and governed.",
                "Auto invention and design output are route-dependent.",
            ],
        ),
        _doc(
            "claire_governance_and_safety",
            "Claire AI Governance and Safety Documentation",
            "governing",
            "governance_contract",
            "current_authority_source",
            "Defines Claire governance model, redline detection, compliance boundaries, oversight, intervention, mode-switching safety, and auditability.",
            ["governance", "safety", "mode_architecture", "update_governance", "evidence"],
            ["governance_gate", "redline_review", "mode_switching"],
            [
                "Governance overrides unsafe behavior.",
                "Mode isolation and auditability are foundational.",
                "Redline scenarios must block or require review.",
            ],
        ),
        _doc(
            "claire_core_pipeline_architecture",
            "Core Pipeline Architecture",
            "canonical",
            "uploaded_pipeline_document",
            "current_pipeline_source",
            "Defines inputs, signal governance, trend discovery, thesis formation, portfolio creation, breakthrough escalation, advancement routing, lifecycle memory, and recursive self-ingestion.",
            ["signal_governance", "trend_discovery", "portfolio", "breakthrough", "acquisition", "recursive_learning"],
            ["signal_to_thesis", "portfolio_path", "breakthrough_gate", "recursive_memory"],
            [
                "Portfolio action is the normal early path.",
                "Breakthrough escalation selects the correct downstream route.",
                "Lifecycle memory enables stronger future runs.",
            ],
        ),
        _doc(
            "claire_lifecycle_spine",
            "Claire 30-Stage Lifecycle / Lifecycle Spine",
            "canonical",
            "uploaded_pipeline_document",
            "current_lifecycle_source",
            "Defines the 30-stage lifecycle from Signal Ingestion through Final Package Construction.",
            ["lifecycle", "route_selection", "evidence"],
            ["all_lifecycle_stages"],
            [
                "Every signal must be processable through the canonical stage contract spine.",
                "Stages 16-22 are critical for route-aware design and buildability outputs.",
                "Stage 30 constructs final packages.",
            ],
        ),
        _doc(
            "claire_branching_master_pipeline",
            "Branching Master Pipeline",
            "canonical",
            "uploaded_pipeline_document",
            "current_route_source",
            "Defines split paths for market/portfolio intelligence and breakthrough/design intelligence after thesis formation.",
            ["route_selection", "portfolio", "breakthrough", "engineering", "acquisition"],
            ["portfolio_path", "breakthrough_design_path", "final_package"],
            [
                "Market and portfolio routes do not require full invention routing.",
                "Breakthrough/design paths continue through buildability, viability, manufacturability, and feasibility.",
            ],
        ),
        _doc(
            "claire_breakthrough_categories",
            "Breakthrough Categories",
            "canonical",
            "uploaded_pipeline_document",
            "current_classification_source",
            "Defines broad breakthrough categories across technology, market, finance, operations, regulation, acquisition, system architecture, evidence, learning loops, and category creation.",
            ["breakthrough", "route_selection", "portfolio", "acquisition", "engineering"],
            ["breakthrough_classification", "advancement_path_selection"],
            [
                "Breakthroughs are structural, not only technological.",
                "Breakthrough classification can drive portfolio, strategy, acquisition, design, or system routes.",
            ],
        ),
        _doc(
            "claire_execution_flow_specification",
            "Claire AI Execution Flow Specification",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines mode initialization, ingestion, semantic processing, hybrid fusion, breakthrough detection, safety pre-validation, scoring, promotion, portfolio creation, and dashboard output.",
            ["mode_architecture", "lifecycle", "governance", "portfolio", "breakthrough", "dashboard"],
            ["mode_initialization", "scoring_validation", "portfolio_creation", "dashboard_output"],
            [
                "Safety and governance override every execution stage.",
                "Connected and hybrid modes activate external ingestion only through governed pathways.",
            ],
        ),
        _doc(
            "claire_hybrid_mode",
            "Claire AI Hybrid Mode",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines Claire's dual-core maximum capability state combining deterministic engine and connected intelligence engine.",
            ["hybrid_mode", "mode_architecture", "engineering", "market", "portfolio", "acquisition"],
            ["hybrid_fusion", "cross_validation", "maximum_capability"],
            [
                "Hybrid mode fuses first-principles reasoning with live intelligence.",
                "Hybrid mode supports cross-validated invention, market, deal, and portfolio intelligence.",
            ],
        ),
        _doc(
            "claire_deterministic_mode",
            "Claire AI Deterministic Mode",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines Claire's air-gapped, reproducible, patent-safe, internal reasoning mode.",
            ["deterministic_mode", "mode_architecture", "safety", "engineering"],
            ["deterministic_reasoning", "air_gapped_logic"],
            [
                "Deterministic mode has no external access.",
                "Deterministic mode is patent-safe and reproducible.",
            ],
        ),
        _doc(
            "claire_connected_intelligence_mode",
            "Claire Connected Intelligence Mode",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines Claire's live market-aware intelligence mode with governed technology, market, competitor, regulatory, and acquisition signals.",
            ["connected_mode", "mode_architecture", "signal_governance", "trend_discovery", "portfolio", "acquisition"],
            ["live_signal_ingestion", "real_time_scanning", "connected_intelligence"],
            [
                "Connected mode uses governed external signal ingestion.",
                "Connected mode supports real-time strategic intelligence and dynamic portfolio optimization.",
            ],
        ),
        _doc(
            "claire_mode_switching_architecture",
            "Claire AI Mode Switching Architecture",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines explicit governed transitions between deterministic, connected, and hybrid modes.",
            ["mode_architecture", "governance", "safety"],
            ["mode_switching", "isolation_reset", "governed_transition"],
            [
                "Claire never switches modes automatically.",
                "Mode transitions require validation and governance checks.",
            ],
        ),
        _doc(
            "claire_full_data_model_map",
            "Claire AI Full Data Model Map",
            "canonical",
            "uploaded_architecture_document",
            "schema_reference",
            "Defines Breakthrough Object, Portfolio Candidate Object, Portfolio Item, signal objects, score objects, safety objects, cluster objects, and mode state.",
            ["data_model", "portfolio", "breakthrough", "evidence", "governance"],
            ["bo", "pco", "portfolio_item", "signal_objects", "safety_objects"],
            [
                "Claire intelligence should use structured objects rather than untyped text blobs.",
                "BO, PCO, and PI are key internal primitives.",
            ],
        ),
        _doc(
            "claire_subsystem_dependency_graph",
            "Claire AI Subsystem Dependency Graph",
            "architectural",
            "uploaded_architecture_document",
            "architecture_reference",
            "Defines dependencies among deterministic engine, connected engine, semantic layer, ingestion layer, hybrid fusion, scoring, portfolio engine, and safety governance.",
            ["mode_architecture", "lifecycle", "portfolio", "breakthrough", "governance"],
            ["dependency_graph", "engine_activation", "safety_layer"],
            [
                "Connected engine cannot run without the safety layer.",
                "Breakthrough detection is the central convergence point.",
            ],
        ),
        _doc(
            "claire_enterprise_update_governance",
            "Claire Enterprise Online Update Governance System",
            "governing",
            "update_governance_contract",
            "current_update_source",
            "Defines safe online update discovery, inspection, scoring, staging, validation, rollback, approval, and refusal rules.",
            ["update_governance", "governance", "safety", "evidence"],
            ["online_update_readiness", "staged_update", "rollback", "approval_gate"],
            [
                "Claire may discover and stage updates online but may not modify active runtime code without validation and approval.",
                "Update flow must be zero-trust, rollback-capable, audit-aware, and regression-resistant.",
            ],
        ),
        _doc(
            "claire_technology_database",
            "Technology Database and Search Dictionary",
            "technical_reference",
            "technology_database_document",
            "technical_reference",
            "Defines technology categories, maturity levels, dependencies, compatibility, cost, complexity, learning curve, performance, and recommendation structures.",
            ["technology_intelligence", "engineering", "design_portal"],
            ["technology_search", "buildability_context", "stack_recommendation"],
            [
                "Claire engineering answers should consider maturity, compatibility, dependency, cost, and integration complexity.",
                "Technology search is a structured intelligence layer, not generic text search.",
            ],
        ),
        _doc(
            "claire_recursive_learning_pipeline",
            "Recursive Learning Pipeline",
            "canonical",
            "uploaded_pipeline_document",
            "current_recursive_source",
            "Defines completed run output storage, lifecycle memory, self-ingestion, pattern comparison, prior output comparison, and stronger future outputs.",
            ["recursive_learning", "evidence", "lifecycle", "system_transformation"],
            ["lifecycle_memory", "recursive_self_ingestion"],
            [
                "Completed runs become future inputs.",
                "Recursive self-ingestion strengthens trend discovery, breakthrough detection, design, portfolio, and package construction.",
            ],
        ),
    ]


def build_s471_knowledge_document_registry() -> Dict[str, Any]:
    docs = build_canonical_knowledge_documents()
    return _safe_base(
        "S471",
        "knowledge_document_registry_ready",
        document_count=len(docs),
        documents=docs,
        doc_ids=[doc["doc_id"] for doc in docs],
        current_authority_note="This registry captures the current canonical Claire knowledge base from uploaded documents.",
    )


def build_domain_ontology() -> Dict[str, Any]:
    docs = build_canonical_knowledge_documents()
    ontology: Dict[str, List[str]] = {tag: [] for tag in DOMAIN_TAGS}
    for doc in docs:
        for domain in doc["domains"]:
            ontology.setdefault(domain, []).append(doc["doc_id"])

    return {
        "domains": DOMAIN_TAGS,
        "domain_to_documents": {key: sorted(value) for key, value in ontology.items() if value},
        "domain_count": len(DOMAIN_TAGS),
    }


def build_s472_domain_ontology_contract() -> Dict[str, Any]:
    ontology = build_domain_ontology()
    return _safe_base(
        "S472",
        "domain_ontology_contract_ready",
        ontology=ontology,
        required_domains=[
            "governance",
            "lifecycle",
            "route_selection",
            "portfolio",
            "breakthrough",
            "acquisition",
            "engineering",
            "technology_intelligence",
            "recursive_learning",
            "update_governance",
        ],
    )


def search_knowledge_registry(query: str | None, domains: Optional[Sequence[str]] = None, limit: int = 6) -> Dict[str, Any]:
    """Deterministic local search over the curated registry."""
    normalized_query = _normalize(query)
    requested_domains = {str(domain) for domain in (domains or []) if str(domain).strip()}
    tokens = [token for token in normalized_query.replace("/", " ").replace("-", " ").split() if len(token) > 2]

    docs = build_canonical_knowledge_documents()
    results: List[Dict[str, Any]] = []

    for doc in docs:
        if requested_domains and not requested_domains.intersection(set(doc["domains"])):
            continue

        haystack_parts = [
            doc["doc_id"],
            doc["title"],
            doc["summary"],
            " ".join(doc["domains"]),
            " ".join(doc["route_anchors"]),
            " ".join(doc["key_claims"]),
        ]
        haystack = _normalize(" ".join(haystack_parts))

        token_hits = [token for token in tokens if token in haystack]
        domain_hits = list(requested_domains.intersection(set(doc["domains"]))) if requested_domains else []

        trust_weight = TRUST_TIERS.get(doc["trust_tier"], TRUST_TIERS["legacy_context"])["weight"]
        score = 0.0
        score += min(0.55, 0.09 * len(token_hits))
        score += min(0.20, 0.08 * len(domain_hits))
        score += trust_weight * 0.20
        if normalized_query and normalized_query in haystack:
            score += 0.15
        if doc["status"].startswith("current"):
            score += 0.05

        score = round(max(0.0, min(1.0, score)), 3)
        if score > 0.15 or not normalized_query:
            results.append(
                {
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "trust_tier": doc["trust_tier"],
                    "score": score,
                    "matched_tokens": token_hits,
                    "matched_domains": domain_hits,
                    "summary": doc["summary"],
                    "route_anchors": doc["route_anchors"],
                    "key_claims": doc["key_claims"],
                }
            )

    results.sort(key=lambda item: (item["score"], TRUST_TIERS.get(item["trust_tier"], {"weight": 0})["weight"]), reverse=True)
    return _safe_base(
        "S473",
        "knowledge_registry_search_complete",
        query=str(query or ""),
        domains=sorted(requested_domains),
        result_count=len(results[:limit]),
        results=results[:limit],
    )


def build_s473_retrieval_contract() -> Dict[str, Any]:
    sample = search_knowledge_registry("governance safety mode switching redline", domains=["governance", "safety"])
    return _safe_base(
        "S473",
        "knowledge_retrieval_contract_ready",
        retrieval_modes=[
            "keyword",
            "domain_filtered",
            "route_anchor_filtered",
            "trust_weighted",
            "local_registry_only",
        ],
        sample_results=sample["results"],
        retrieval_limits=[
            "This is deterministic registry retrieval, not vector search.",
            "It does not read external files or perform live web search.",
            "Future versions may attach file-backed evidence excerpts through governed evidence routes.",
        ],
    )


def build_route_anchor_map() -> Dict[str, List[str]]:
    docs = build_canonical_knowledge_documents()
    route_map: Dict[str, List[str]] = {}
    for doc in docs:
        for route in doc["route_anchors"]:
            route_map.setdefault(route, []).append(doc["doc_id"])
    return {key: sorted(value) for key, value in sorted(route_map.items())}


def build_s474_route_anchor_contract() -> Dict[str, Any]:
    route_map = build_route_anchor_map()
    return _safe_base(
        "S474",
        "route_anchor_contract_ready",
        route_anchor_map=route_map,
        required_route_anchors=[
            "signal_to_portfolio",
            "breakthrough_escalation",
            "portfolio_path",
            "breakthrough_design_path",
            "final_package",
            "recursive_self_ingestion",
            "online_update_readiness",
        ],
    )


def build_s475_source_trust_and_freshness_contract() -> Dict[str, Any]:
    docs = build_canonical_knowledge_documents()
    trust_counts: Dict[str, int] = {}
    stale_or_legacy: List[str] = []
    for doc in docs:
        trust_counts[doc["trust_tier"]] = trust_counts.get(doc["trust_tier"], 0) + 1
        if doc["status"] in {"legacy_context", "outdated"}:
            stale_or_legacy.append(doc["doc_id"])

    return _safe_base(
        "S475",
        "source_trust_and_freshness_contract_ready",
        trust_tiers=TRUST_TIERS,
        trust_counts=trust_counts,
        stale_or_legacy_docs=stale_or_legacy,
        rules=[
            "Governing documents override legacy context.",
            "Current compiled platform definition and master build plan are highest priority for identity and roadmap.",
            "Governance and safety documents override convenience or speed.",
            "Technology references inform engineering but do not override lifecycle governance.",
        ],
    )


def build_s476_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S476",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "knowledge_base_registry_panel",
            "document_source_cards",
            "domain_ontology_map",
            "route_anchor_map",
            "source_trust_badges",
        ],
        visual_authority="presentation_only",
    )


def registry_documents_as_evidence_sources(domains: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """Convert registry documents to evidence-source dicts compatible with S464-S470."""
    from claire.api import claire_evidence_backed_answer_model_s464_s470 as evidence_model

    requested_domains = {str(domain) for domain in (domains or []) if str(domain).strip()}
    docs = build_canonical_knowledge_documents()
    sources = []
    for doc in docs:
        if requested_domains and not requested_domains.intersection(set(doc["domains"])):
            continue
        trust_weight = TRUST_TIERS.get(doc["trust_tier"], TRUST_TIERS["legacy_context"])["weight"]
        source_type = {
            "governing": "uploaded_master_document",
            "canonical": "uploaded_pipeline_document",
            "architectural": "uploaded_architecture_document",
            "technical_reference": "technology_database_document",
            "legacy_context": "general_context",
        }.get(doc["trust_tier"], "general_context")
        sources.append(
            evidence_model.make_evidence_source(
                source_id=doc["doc_id"],
                title=doc["title"],
                source_type=source_type,
                summary=doc["summary"],
                relevance=0.84,
                specificity=0.82,
                trust=trust_weight,
                recency=0.78 if doc["status"].startswith("current") else 0.62,
                supports=doc["key_claims"],
                limitations=doc["limitations"],
            )
        )
    return sources


def build_s477_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s471 = build_s471_knowledge_document_registry()
    s472 = build_s472_domain_ontology_contract()
    s473 = build_s473_retrieval_contract()
    s474 = build_s474_route_anchor_contract()
    s475 = build_s475_source_trust_and_freshness_contract()
    s476 = build_s476_cockpit_asset_manifest(project_root)

    gov_search = search_knowledge_registry("governance safety redline mode switching", domains=["governance", "safety"])
    portfolio_search = search_knowledge_registry("portfolio trend discovery thesis route", domains=["portfolio", "trend_discovery"])
    update_search = search_knowledge_registry("online update rollback approval staged validation", domains=["update_governance"])
    evidence_sources = registry_documents_as_evidence_sources(domains=["governance"])

    checks = {
        "s471_registry_has_enough_documents": s471["document_count"] >= 15,
        "s472_ontology_has_required_domains": all(domain in s472["ontology"]["domain_to_documents"] for domain in ["governance", "lifecycle", "portfolio", "breakthrough"]),
        "s473_retrieval_returns_governance": any(result["doc_id"] == "claire_governance_and_safety" for result in gov_search["results"]),
        "s474_route_map_has_core_routes": all(route in s474["route_anchor_map"] for route in ["portfolio_path", "breakthrough_design_path", "recursive_self_ingestion"]),
        "s475_has_governing_trust_tier": s475["trust_counts"].get("governing", 0) >= 3,
        "s476_assets_exist": s476["assets"]["js_exists"] is True and s476["assets"]["css_exists"] is True,
        "portfolio_search_finds_pipeline": any("portfolio" in result["doc_id"] or "pipeline" in result["doc_id"] for result in portfolio_search["results"]),
        "update_search_finds_update_governance": any(result["doc_id"] == "claire_enterprise_update_governance" for result in update_search["results"]),
        "registry_exports_evidence_sources": len(evidence_sources) >= 1 and all("source_id" in source for source in evidence_sources),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S477",
        "claire_knowledge_base_registry_passed" if ok else "claire_knowledge_base_registry_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_searches={
            "governance": gov_search,
            "portfolio": portfolio_search,
            "update_governance": update_search,
        },
        evidence_source_count=len(evidence_sources),
        forward_motion_allowed=ok,
        next_phase="S478-S484 Market / research / engineering answer routes",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s477_claire_knowledge_base_registry_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_knowledge_base_registry_s471_s477(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S471-S477",
        "claire_knowledge_base_registry_ready",
        contracts={
            "s471": build_s471_knowledge_document_registry(),
            "s472": build_s472_domain_ontology_contract(),
            "s473": build_s473_retrieval_contract(),
            "s474": build_s474_route_anchor_contract(),
            "s475": build_s475_source_trust_and_freshness_contract(),
            "s476": build_s476_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s477_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "TRUST_TIERS",
    "DOMAIN_TAGS",
    "build_canonical_knowledge_documents",
    "build_s471_knowledge_document_registry",
    "build_domain_ontology",
    "build_s472_domain_ontology_contract",
    "search_knowledge_registry",
    "build_s473_retrieval_contract",
    "build_route_anchor_map",
    "build_s474_route_anchor_contract",
    "build_s475_source_trust_and_freshness_contract",
    "build_s476_cockpit_asset_manifest",
    "registry_documents_as_evidence_sources",
    "build_s477_stop_gate",
    "build_claire_knowledge_base_registry_s471_s477",
]
