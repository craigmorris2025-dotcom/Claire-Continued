from __future__ import annotations

"""
Claire Domain Answer Routes — S478-S484

This module builds the first specialized Claire answer routes for:
- Market Intelligence
- Research Intelligence
- Engineering Intelligence
- Cross-domain synthesis between those routes

It builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Response Cards
- S464-S470 Evidence-Backed Answer Model
- S471-S477 Claire Knowledge Base Registry

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, or autonomous execution are performed here.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


VERSION = "v19.89.8-S478-S484"
PHASE = "S478-S484"
JS_ASSET = "frontend/cockpit/shell/assets/claire_domain_answer_routes.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_domain_answer_routes.css"


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


DOMAIN_ROUTES: Dict[str, Dict[str, Any]] = {
    "market": {
        "label": "Market Intelligence Route",
        "route_id": "market_intelligence_route",
        "primary_goal": "Translate signals into market reality, timing, competitive pressure, demand logic, and portfolio implication.",
        "knowledge_domains": ["market", "trend_discovery", "portfolio", "acquisition"],
        "route_outputs": [
            "market_reality",
            "trend_signal_read",
            "competitive_pressure",
            "timing_window",
            "portfolio_implication",
            "verification_needs",
        ],
    },
    "research": {
        "label": "Research Intelligence Route",
        "route_id": "research_intelligence_route",
        "primary_goal": "Separate evidence, assumptions, inference, uncertainty, and verification requirements.",
        "knowledge_domains": ["research", "evidence", "technology_intelligence", "governance"],
        "route_outputs": [
            "evidence_summary",
            "source_quality",
            "knowns_unknowns",
            "claim_support",
            "verification_plan",
        ],
    },
    "engineering": {
        "label": "Engineering Intelligence Route",
        "route_id": "engineering_intelligence_route",
        "primary_goal": "Assess buildability, dependencies, constraints, feasibility, implementation path, and design-route potential.",
        "knowledge_domains": ["engineering", "technology_intelligence", "design_portal", "lifecycle", "breakthrough"],
        "route_outputs": [
            "buildability_read",
            "dependency_map",
            "constraint_notes",
            "feasibility_questions",
            "design_route_potential",
            "verification_needs",
        ],
    },
    "cross_domain": {
        "label": "Cross-Domain Synthesis Route",
        "route_id": "cross_domain_synthesis_route",
        "primary_goal": "Combine market, research, and engineering intelligence into a route-aware synthesis.",
        "knowledge_domains": ["market", "research", "engineering", "portfolio", "breakthrough", "acquisition"],
        "route_outputs": [
            "synthesis",
            "conflicts",
            "alignment",
            "innovation_angle",
            "route_recommendation",
            "verification_needs",
        ],
    },
}


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


def _load_answer_contract_module():
    from claire.api import claire_intelligence_answer_contract_s450_s456 as answer_contract

    return answer_contract


def _load_evidence_model_module():
    from claire.api import claire_evidence_backed_answer_model_s464_s470 as evidence_model

    return evidence_model


def _load_kb_module():
    from claire.api import claire_knowledge_base_registry_s471_s477 as kb_registry

    return kb_registry


def infer_domain_route(question: str | None, preferred_domain: str | None = None) -> Dict[str, Any]:
    """Infer one of market/research/engineering/cross_domain from the question and S450 classifier."""
    normalized = _normalize(question)
    preferred = _normalize(preferred_domain)

    if preferred in {"market", "research", "engineering", "cross_domain"}:
        selected = preferred
    else:
        answer_contract = _load_answer_contract_module()
        classification = answer_contract.classify_claire_question(question)
        domain = classification.get("domain", "general")

        market_terms = ["market", "demand", "pricing", "customer", "competitor", "competitive", "tam", "sam", "som", "trend"]
        research_terms = ["research", "paper", "study", "source", "evidence", "verify", "document", "patent", "literature"]
        engineering_terms = ["engineering", "build", "buildable", "architecture", "component", "dependency", "manufacture", "deploy", "feasible", "prototype"]

        matched_groups = {
            "market": [term for term in market_terms if term in normalized],
            "research": [term for term in research_terms if term in normalized],
            "engineering": [term for term in engineering_terms if term in normalized],
        }
        active_groups = [key for key, hits in matched_groups.items() if hits]

        if len(active_groups) >= 2:
            selected = "cross_domain"
        elif domain in {"market", "research", "engineering"}:
            selected = domain
        elif active_groups:
            selected = active_groups[0]
        else:
            selected = "cross_domain"

    profile = DOMAIN_ROUTES[selected]
    return {
        "selected_domain_route": selected,
        "route_id": profile["route_id"],
        "label": profile["label"],
        "knowledge_domains": profile["knowledge_domains"],
        "primary_goal": profile["primary_goal"],
    }


def build_s478_market_answer_route_contract() -> Dict[str, Any]:
    return _safe_base(
        "S478",
        "market_answer_route_contract_ready",
        route=DOMAIN_ROUTES["market"],
        method=[
            "Classify market-oriented question.",
            "Retrieve market, trend, portfolio, and acquisition knowledge anchors.",
            "Build evidence-backed answer.",
            "Separate market reality, assumptions, and verification needs.",
        ],
        market_answer_sections=[
            "direct_market_read",
            "trend_signal_read",
            "demand_logic",
            "competitive_pressure",
            "timing_window",
            "portfolio_implication",
            "verification_needs",
        ],
    )


def build_s479_research_answer_route_contract() -> Dict[str, Any]:
    return _safe_base(
        "S479",
        "research_answer_route_contract_ready",
        route=DOMAIN_ROUTES["research"],
        method=[
            "Classify research-oriented question.",
            "Retrieve evidence, research, technology, and governance knowledge anchors.",
            "Build evidence-backed answer.",
            "Separate facts, assumptions, inferences, and verification needs.",
        ],
        research_answer_sections=[
            "evidence_summary",
            "source_quality",
            "supported_claims",
            "assumptions",
            "inferences",
            "unknowns",
            "verification_plan",
        ],
    )


def build_s480_engineering_answer_route_contract() -> Dict[str, Any]:
    return _safe_base(
        "S480",
        "engineering_answer_route_contract_ready",
        route=DOMAIN_ROUTES["engineering"],
        method=[
            "Classify engineering-oriented question.",
            "Retrieve engineering, technology, design portal, lifecycle, and breakthrough knowledge anchors.",
            "Build evidence-backed answer.",
            "Assess buildability, constraints, dependencies, and design-route potential.",
        ],
        engineering_answer_sections=[
            "buildability_read",
            "architecture_implications",
            "dependencies",
            "constraints",
            "feasibility_questions",
            "design_route_potential",
            "verification_needs",
        ],
    )


def _knowledge_results_for_route(route_key: str, question: str | None) -> Dict[str, Any]:
    kb = _load_kb_module()
    domains = DOMAIN_ROUTES[route_key]["knowledge_domains"]
    return kb.search_knowledge_registry(question or DOMAIN_ROUTES[route_key]["primary_goal"], domains=domains, limit=6)


def _evidence_sources_for_route(route_key: str) -> List[Dict[str, Any]]:
    kb = _load_kb_module()
    domains = DOMAIN_ROUTES[route_key]["knowledge_domains"]
    return kb.registry_documents_as_evidence_sources(domains=domains)


def _route_specific_sections(route_key: str, question: str | None, evidence_answer: Dict[str, Any], knowledge_results: Dict[str, Any]) -> Dict[str, Any]:
    support_level = evidence_answer.get("confidence_basis", {}).get("support_level", "unknown")
    route_hint = evidence_answer.get("route_hint", DOMAIN_ROUTES[route_key]["route_id"])
    result_titles = [item["title"] for item in knowledge_results.get("results", [])[:4]]

    if route_key == "market":
        return {
            "direct_market_read": "Assess the question through trend strength, demand logic, competition, timing, and portfolio implication.",
            "trend_signal_read": "Use signal governance and trend-discovery anchors before treating a market observation as actionable.",
            "demand_logic": "Check whether the signal implies latent demand, rising demand, pricing power, or customer behavior change.",
            "competitive_pressure": "Map visible competitors, category pressure, displacement risk, and timing windows.",
            "portfolio_implication": "Translate the market read into exposure, weighting, watchlist, or action recommendation only after evidence passes threshold.",
            "verification_needs": evidence_answer.get("verification_needed", []),
            "knowledge_sources": result_titles,
            "support_level": support_level,
            "route_hint": route_hint,
        }

    if route_key == "research":
        return {
            "evidence_summary": "Use the evidence basket to identify which claims are supported, partially supported, inferred, assumed, or unverified.",
            "source_quality": "Prioritize governing, canonical, architectural, and technical-reference sources over legacy context.",
            "knowns_unknowns": "Separate known platform facts from open verification questions.",
            "claim_support": evidence_answer.get("claims", []),
            "verification_plan": evidence_answer.get("verification_needed", []),
            "knowledge_sources": result_titles,
            "support_level": support_level,
            "route_hint": route_hint,
        }

    if route_key == "engineering":
        return {
            "buildability_read": "Assess whether the concept can be structured into components, dependencies, constraints, and implementation phases.",
            "architecture_implications": "Use lifecycle stages 16-22 and technology-intelligence references before calling the design route ready.",
            "dependencies": "Identify missing components, technology stack requirements, compatibility constraints, and integration complexity.",
            "constraints": "Evaluate feasibility, manufacturability/deployability, regulatory constraints, cost, and proof requirements.",
            "design_route_potential": bool(evidence_answer.get("innovation_potential")) or "design_portal" in DOMAIN_ROUTES[route_key]["knowledge_domains"],
            "verification_needs": evidence_answer.get("verification_needed", []),
            "knowledge_sources": result_titles,
            "support_level": support_level,
            "route_hint": route_hint,
        }

    return {
        "synthesis": "Combine market timing, research evidence, and engineering feasibility before selecting an advancement path.",
        "conflicts": "Flag cases where market opportunity is high but evidence or buildability is weak.",
        "alignment": "A strong route requires demand logic, source support, and feasibility to point in the same direction.",
        "innovation_angle": bool(evidence_answer.get("innovation_potential")),
        "route_recommendation": route_hint,
        "verification_needs": evidence_answer.get("verification_needed", []),
        "knowledge_sources": result_titles,
        "support_level": support_level,
    }


def build_domain_answer_route(
    question: str | None,
    preferred_domain: str | None = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a specialized market/research/engineering/cross-domain answer route."""
    route_selection = infer_domain_route(question, preferred_domain=preferred_domain)
    route_key = route_selection["selected_domain_route"]

    evidence_model = _load_evidence_model_module()
    sources = _evidence_sources_for_route(route_key)
    evidence_answer = evidence_model.build_evidence_backed_answer(question, sources=sources, context=context or {})
    knowledge_results = _knowledge_results_for_route(route_key, question)

    route_sections = _route_specific_sections(route_key, question, evidence_answer, knowledge_results)

    result = {
        "version": VERSION,
        "created_at": _now(),
        "question": str(question or ""),
        "route_selection": route_selection,
        "route_profile": DOMAIN_ROUTES[route_key],
        "evidence_answer": evidence_answer,
        "knowledge_results": knowledge_results,
        "route_sections": route_sections,
        "answer_quality_state": evidence_answer.get("answer_quality_state"),
        "confidence": evidence_answer.get("confidence"),
        "safe_next_operator_actions": [
            "review_evidence_basket",
            "inspect_knowledge_sources",
            "request_governed_research_if_needed",
            "route_to_lifecycle_runtime_only_after_operator_review",
        ],
    }
    result.update(BLOCKED_AUTHORITY)
    return result


def build_s481_cross_domain_synthesis_contract() -> Dict[str, Any]:
    sample = build_domain_answer_route(
        "Can Claire compare market demand, research evidence, and engineering buildability for this opportunity?"
    )
    return _safe_base(
        "S481",
        "cross_domain_synthesis_contract_ready",
        route=DOMAIN_ROUTES["cross_domain"],
        synthesis_rules=[
            "Do not treat market opportunity alone as proof of buildability.",
            "Do not treat technical feasibility alone as proof of demand.",
            "Do not treat weak evidence as a strong recommendation.",
            "Escalate to breakthrough or design routes only when evidence, market logic, and feasibility align.",
        ],
        sample_route=sample["route_selection"],
    )


def build_s482_domain_route_response_builder_contract() -> Dict[str, Any]:
    sample_market = build_domain_answer_route("Can Claire analyze this market trend and pricing opportunity?", preferred_domain="market")
    sample_engineering = build_domain_answer_route("Is this architecture buildable and feasible?", preferred_domain="engineering")
    return _safe_base(
        "S482",
        "domain_route_response_builder_ready",
        builder="build_domain_answer_route",
        supported_routes=sorted(DOMAIN_ROUTES.keys()),
        sample_outputs={
            "market": {
                "route": sample_market["route_selection"],
                "confidence": sample_market["confidence"],
                "quality": sample_market["answer_quality_state"],
            },
            "engineering": {
                "route": sample_engineering["route_selection"],
                "confidence": sample_engineering["confidence"],
                "quality": sample_engineering["answer_quality_state"],
            },
        },
    )


def build_s483_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S483",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "domain_route_panel",
            "market_answer_route_card",
            "research_answer_route_card",
            "engineering_answer_route_card",
            "cross_domain_synthesis_card",
            "route_evidence_summary",
        ],
        visual_authority="presentation_only",
    )


def build_s484_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s478 = build_s478_market_answer_route_contract()
    s479 = build_s479_research_answer_route_contract()
    s480 = build_s480_engineering_answer_route_contract()
    s481 = build_s481_cross_domain_synthesis_contract()
    s482 = build_s482_domain_route_response_builder_contract()
    s483 = build_s483_cockpit_asset_manifest(project_root)

    market = build_domain_answer_route("Can Claire analyze this market trend and demand signal?", preferred_domain="market")
    research = build_domain_answer_route("Can Claire review the research evidence and source quality?", preferred_domain="research")
    engineering = build_domain_answer_route("Can Claire assess if this system architecture is buildable?", preferred_domain="engineering")
    cross = build_domain_answer_route("Can Claire compare market demand, research evidence, and engineering feasibility?")

    checks = {
        "s478_market_route_ready": s478["route"]["route_id"] == "market_intelligence_route",
        "s479_research_route_ready": s479["route"]["route_id"] == "research_intelligence_route",
        "s480_engineering_route_ready": s480["route"]["route_id"] == "engineering_intelligence_route",
        "s481_cross_domain_ready": s481["sample_route"]["selected_domain_route"] == "cross_domain",
        "s482_builder_ready": "market" in s482["supported_routes"] and "engineering" in s482["supported_routes"],
        "s483_assets_exist": s483["assets"]["js_exists"] is True and s483["assets"]["css_exists"] is True,
        "market_output_safe": market["route_selection"]["selected_domain_route"] == "market" and all(market.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "research_output_safe": research["route_selection"]["selected_domain_route"] == "research" and all(research.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "engineering_output_safe": engineering["route_selection"]["selected_domain_route"] == "engineering" and all(engineering.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "cross_domain_output_safe": cross["route_selection"]["selected_domain_route"] == "cross_domain" and all(cross.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S484",
        "claire_domain_answer_routes_passed" if ok else "claire_domain_answer_routes_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "market": market,
            "research": research,
            "engineering": engineering,
            "cross_domain": cross,
        },
        forward_motion_allowed=ok,
        next_phase="S485-S491 Innovation potential detection and route escalation",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s484_claire_domain_answer_routes_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_domain_answer_routes_s478_s484(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S478-S484",
        "claire_domain_answer_routes_ready",
        contracts={
            "s478": build_s478_market_answer_route_contract(),
            "s479": build_s479_research_answer_route_contract(),
            "s480": build_s480_engineering_answer_route_contract(),
            "s481": build_s481_cross_domain_synthesis_contract(),
            "s482": build_s482_domain_route_response_builder_contract(),
            "s483": build_s483_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s484_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "DOMAIN_ROUTES",
    "infer_domain_route",
    "build_domain_answer_route",
    "build_s478_market_answer_route_contract",
    "build_s479_research_answer_route_contract",
    "build_s480_engineering_answer_route_contract",
    "build_s481_cross_domain_synthesis_contract",
    "build_s482_domain_route_response_builder_contract",
    "build_s483_cockpit_asset_manifest",
    "build_s484_stop_gate",
    "build_claire_domain_answer_routes_s478_s484",
]
