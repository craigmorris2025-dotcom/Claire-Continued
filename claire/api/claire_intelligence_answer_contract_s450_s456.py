from __future__ import annotations

"""
Claire Intelligence Answer Contract — S450-S456

This module creates the first governed Claire Q&A / command-response
foundation without enabling autonomous execution, runtime mutation,
automatic updates, uncontrolled crawling, or live web action.

It is a read-only intelligence contract layer:
- classify the operator question
- identify the intelligence domain
- define the evidence requirement
- define the answer shape
- identify possible innovation/route potential
- preserve all governance authority blocks
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S450-S456"
PHASE = "S450-S456"
JS_ASSET = "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_intelligence_answer_contract.css"


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


DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "governance": [
        "governance",
        "safety",
        "blocked",
        "redline",
        "compliance",
        "authority",
        "risk gate",
        "approval",
        "rollback",
    ],
    "portfolio": [
        "portfolio",
        "allocation",
        "weighting",
        "exposure",
        "rebalance",
        "optimize",
        "holdings",
        "position",
    ],
    "breakthrough": [
        "breakthrough",
        "invention",
        "invent",
        "novel",
        "disruptive",
        "category creation",
        "white space",
        "gap",
    ],
    "acquisition": [
        "acquisition",
        "acquirer",
        "buyer",
        "m&a",
        "deal",
        "strategic fit",
        "exit",
        "package",
    ],
    "engineering": [
        "engineering",
        "build",
        "buildable",
        "architecture",
        "manufacturing",
        "deploy",
        "system design",
        "component",
        "feasibility",
        "prototype",
        "technical",
    ],
    "market": [
        "market",
        "tam",
        "sam",
        "som",
        "competitor",
        "competitive",
        "pricing",
        "demand",
        "customer",
        "trend",
        "industry",
    ],
    "research": [
        "research",
        "paper",
        "study",
        "evidence",
        "source",
        "document",
        "literature",
        "patent",
        "journal",
        "data",
    ],
    "general": [],
}


DOMAIN_PROFILES: Dict[str, Dict[str, Any]] = {
    "general": {
        "label": "General Question",
        "answer_goal": "Give a clear direct answer, then offer useful context when needed.",
        "evidence_requirement": "low_or_contextual",
        "default_route": "general_answer",
    },
    "market": {
        "label": "Market Intelligence",
        "answer_goal": "Explain market reality, demand signals, competition, timing, and practical implications.",
        "evidence_requirement": "moderate_to_high",
        "default_route": "trend_or_portfolio_path",
    },
    "research": {
        "label": "Research Intelligence",
        "answer_goal": "Summarize evidence, identify source quality, compare interpretations, and separate fact from inference.",
        "evidence_requirement": "high",
        "default_route": "research_answer",
    },
    "engineering": {
        "label": "Engineering Intelligence",
        "answer_goal": "Assess buildability, dependencies, architecture, constraints, risks, and realistic implementation path.",
        "evidence_requirement": "moderate_to_high",
        "default_route": "engineering_feasibility_path",
    },
    "portfolio": {
        "label": "Portfolio Intelligence",
        "answer_goal": "Translate signals into thesis, exposure, weighting, risk, and action recommendations.",
        "evidence_requirement": "high",
        "default_route": "portfolio_creation_or_optimization",
    },
    "breakthrough": {
        "label": "Breakthrough Intelligence",
        "answer_goal": "Evaluate whether a discovery meets breakthrough criteria and identify the correct advancement route.",
        "evidence_requirement": "high",
        "default_route": "breakthrough_escalation_gate",
    },
    "acquisition": {
        "label": "Acquisition Intelligence",
        "answer_goal": "Assess acquirer fit, strategic rationale, value capture, timing, and package-readiness.",
        "evidence_requirement": "high",
        "default_route": "acquisition_fit_and_package",
    },
    "governance": {
        "label": "Governance / Safety",
        "answer_goal": "Explain authority boundaries, blocked actions, safety state, rollback needs, and approval requirements.",
        "evidence_requirement": "contractual",
        "default_route": "governance_status",
    },
}


@dataclass(frozen=True)
class ClaireQuestionClassification:
    question: str
    domain: str
    label: str
    confidence: float
    matched_keywords: List[str]
    evidence_requirement: str
    default_route: str
    innovation_potential: bool
    answer_mode: str


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


def classify_claire_question(question: str | None) -> Dict[str, Any]:
    """Deterministically classify a Claire operator/user question."""
    normalized = _normalize(question)
    if not normalized:
        profile = DOMAIN_PROFILES["general"]
        classification = ClaireQuestionClassification(
            question="",
            domain="general",
            label=profile["label"],
            confidence=0.0,
            matched_keywords=[],
            evidence_requirement=profile["evidence_requirement"],
            default_route=profile["default_route"],
            innovation_potential=False,
            answer_mode="waiting_for_question",
        )
        return asdict(classification)

    scores: Dict[str, List[str]] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if domain == "general":
            continue
        matches = [kw for kw in keywords if kw in normalized]
        if matches:
            scores[domain] = matches

    priority = [
        "governance",
        "portfolio",
        "breakthrough",
        "acquisition",
        "engineering",
        "market",
        "research",
    ]

    domain = "general"
    matched: List[str] = []
    for candidate in priority:
        if candidate in scores:
            domain = candidate
            matched = scores[candidate]
            break

    profile = DOMAIN_PROFILES[domain]
    confidence = 0.45 if domain == "general" else min(0.95, 0.62 + 0.08 * len(matched))

    innovation_terms = [
        "innovation",
        "innovate",
        "breakthrough",
        "invent",
        "design",
        "build",
        "system",
        "gap",
        "new",
        "novel",
        "better",
        "optimize",
    ]
    innovation_potential = any(term in normalized for term in innovation_terms) and domain in {
        "market",
        "research",
        "engineering",
        "portfolio",
        "breakthrough",
        "acquisition",
        "general",
    }

    classification = ClaireQuestionClassification(
        question=str(question or ""),
        domain=domain,
        label=profile["label"],
        confidence=round(confidence, 2),
        matched_keywords=matched,
        evidence_requirement=profile["evidence_requirement"],
        default_route=profile["default_route"],
        innovation_potential=innovation_potential,
        answer_mode="governed_intelligence_answer",
    )
    return asdict(classification)


def build_s450_question_classification_contract() -> Dict[str, Any]:
    return _safe_base(
        "S450",
        "question_classification_contract_ready",
        classifier="deterministic_keyword_and_priority_router",
        supported_domains=sorted(DOMAIN_PROFILES.keys()),
        classification_fields=[
            "question",
            "domain",
            "label",
            "confidence",
            "matched_keywords",
            "evidence_requirement",
            "default_route",
            "innovation_potential",
            "answer_mode",
        ],
        notes=[
            "This is the safe foundation for Claire Q&A.",
            "It does not call an external model.",
            "It does not perform live web requests.",
            "It does not mutate runtime truth.",
        ],
    )


def build_s451_domain_intelligence_profiles() -> Dict[str, Any]:
    return _safe_base(
        "S451",
        "domain_intelligence_profiles_ready",
        domain_profiles={k: dict(v) for k, v in DOMAIN_PROFILES.items()},
        default_domain="general",
        high_value_domains=[
            "market",
            "research",
            "engineering",
            "portfolio",
            "breakthrough",
            "acquisition",
        ],
        claire_identity="Cognitive Learning Artificial Intelligence Research Engineering",
    )


def build_s452_answer_shape_contract() -> Dict[str, Any]:
    return _safe_base(
        "S452",
        "answer_shape_contract_ready",
        answer_sections=[
            "direct_answer",
            "classification",
            "what_supports_it",
            "engineering_or_market_reality",
            "assumptions",
            "confidence",
            "innovation_potential",
            "recommended_next_verification",
            "governance_state",
        ],
        required_output_fields=[
            "answer_id",
            "question",
            "classification",
            "direct_answer",
            "supporting_context",
            "assumptions",
            "confidence",
            "innovation_potential",
            "route_hint",
            "evidence_requirement",
            "governance_state",
        ],
    )


def build_s453_evidence_requirement_contract() -> Dict[str, Any]:
    return _safe_base(
        "S453",
        "evidence_requirement_contract_ready",
        evidence_levels={
            "low_or_contextual": "Accepts general reasoning but should disclose uncertainty.",
            "moderate_to_high": "Requires supporting context, constraints, and practical checks.",
            "high": "Requires evidence-backed reasoning before strong claims or route escalation.",
            "contractual": "Requires system contract, safety, governance, or runtime-state evidence.",
        },
        evidence_behavior=[
            "Do not pretend unsupported answers are proven.",
            "Separate facts, assumptions, inferences, and recommendations.",
            "Use live search only through governed search routes when enabled.",
            "Until live routes are explicitly authorized, answer from internal context and available evidence.",
        ],
    )


def build_s454_innovation_route_potential_contract() -> Dict[str, Any]:
    return _safe_base(
        "S454",
        "innovation_route_potential_contract_ready",
        route_logic={
            "general": "general_answer_or_clarifying_context",
            "market": "trend_discovery_or_portfolio_path",
            "research": "evidence_review_or_discovery_generation",
            "engineering": "buildability_or_design_feasibility_path",
            "portfolio": "portfolio_creation_or_optimization",
            "breakthrough": "breakthrough_escalation_gate",
            "acquisition": "acquirer_fit_or_final_package_path",
            "governance": "governance_status_or_safety_gate",
        },
        innovation_detection_inputs=[
            "question keywords",
            "domain classification",
            "evidence requirement",
            "route hint",
            "operator intent",
        ],
        route_authority_note="Route hints are advisory until an approved lifecycle runtime executes them.",
    )


def build_s455_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S455",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "permanent_search_bar",
            "claire_response_panel",
            "classification_badge",
            "evidence_requirement_badge",
            "innovation_potential_indicator",
            "governance_state_footer",
        ],
        visual_authority="presentation_only",
    )


def build_claire_intelligence_answer(question: str | None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a governed answer contract for a question without performing external actions."""
    classification = classify_claire_question(question)
    domain = classification["domain"]
    profile = DOMAIN_PROFILES[domain]

    if not classification["question"]:
        direct_answer = "Claire is waiting for an operator question."
        confidence = 0.0
        assumptions: List[str] = []
    else:
        direct_answer = (
            f"Claire classified this as {profile['label']} and would answer using the "
            f"{profile['default_route']} route with {profile['evidence_requirement']} evidence requirements."
        )
        confidence = classification["confidence"]
        assumptions = [
            "This response is a governed answer contract, not a live external research result.",
            "No runtime mutation, live web action, or autonomous execution was performed.",
        ]

    governance_state = {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        **BLOCKED_AUTHORITY,
    }

    answer = {
        "answer_id": f"claire_answer_{abs(hash((classification['question'], domain))) % 10_000_000:07d}",
        "version": VERSION,
        "created_at": _now(),
        "question": classification["question"],
        "classification": classification,
        "direct_answer": direct_answer,
        "supporting_context": {
            "profile": dict(profile),
            "provided_context_keys": sorted((context or {}).keys()),
            "contractual_basis": "Claire Syntalion intelligence-routed Q&A foundation",
        },
        "assumptions": assumptions,
        "confidence": confidence,
        "innovation_potential": classification["innovation_potential"],
        "route_hint": profile["default_route"],
        "evidence_requirement": profile["evidence_requirement"],
        "recommended_next_verification": [
            "Check available internal evidence.",
            "If live research is required, route through governed web evidence workflow.",
            "If route escalation is needed, use lifecycle runtime rather than direct mutation.",
        ],
        "governance_state": governance_state,
    }
    answer.update(BLOCKED_AUTHORITY)
    return answer


def build_s456_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s450 = build_s450_question_classification_contract()
    s451 = build_s451_domain_intelligence_profiles()
    s452 = build_s452_answer_shape_contract()
    s453 = build_s453_evidence_requirement_contract()
    s454 = build_s454_innovation_route_potential_contract()
    s455 = build_s455_cockpit_asset_manifest(project_root)
    sample_answer = build_claire_intelligence_answer(
        "Can Claire evaluate this market trend and identify an innovation route?"
    )

    checks = {
        "s450_ready": s450["ready"] is True,
        "s451_profiles_ready": s451["ready"] is True and "engineering" in s451["domain_profiles"],
        "s452_answer_shape_ready": "direct_answer" in s452["answer_sections"],
        "s453_evidence_contract_ready": "high" in s453["evidence_levels"],
        "s454_route_contract_ready": "breakthrough" in s454["route_logic"],
        "s455_assets_exist": s455["assets"]["js_exists"] is True and s455["assets"]["css_exists"] is True,
        "sample_answer_safe": all(sample_answer.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "sample_answer_classified": sample_answer["classification"]["domain"] in DOMAIN_PROFILES,
    }

    ok = all(checks.values())
    result = _safe_base(
        "S456",
        "claire_intelligence_answer_contract_passed" if ok else "claire_intelligence_answer_contract_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_answer=sample_answer,
        forward_motion_allowed=ok,
        next_phase="S457-S463 Claire command classification and response cards",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s456_claire_intelligence_answer_contract_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_intelligence_answer_contract_s450_s456(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S450-S456",
        "claire_intelligence_answer_contract_ready",
        contracts={
            "s450": build_s450_question_classification_contract(),
            "s451": build_s451_domain_intelligence_profiles(),
            "s452": build_s452_answer_shape_contract(),
            "s453": build_s453_evidence_requirement_contract(),
            "s454": build_s454_innovation_route_potential_contract(),
            "s455": build_s455_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s456_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "DOMAIN_PROFILES",
    "classify_claire_question",
    "build_claire_intelligence_answer",
    "build_s450_question_classification_contract",
    "build_s451_domain_intelligence_profiles",
    "build_s452_answer_shape_contract",
    "build_s453_evidence_requirement_contract",
    "build_s454_innovation_route_potential_contract",
    "build_s455_cockpit_asset_manifest",
    "build_s456_stop_gate",
    "build_claire_intelligence_answer_contract_s450_s456",
]
