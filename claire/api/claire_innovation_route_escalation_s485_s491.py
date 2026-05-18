from __future__ import annotations

"""
Claire Innovation Potential Detection and Route Escalation — S485-S491

This module builds the first governed innovation-potential detector and
route-escalation model for Claire answers.

It builds on:
- S450-S456 Claire Intelligence Answer Contract
- S457-S463 Claire Command Response Cards
- S464-S470 Evidence-Backed Answer Model
- S471-S477 Claire Knowledge Base Registry
- S478-S484 Market / Research / Engineering Answer Routes

Purpose:
- detect innovation potential from question + route/evidence context
- score escalation categories deterministically
- recommend route candidates without executing them
- preserve governance and route authority
- block autonomous escalation, mutation, automatic updates, live web execution,
  and uncontrolled crawling

No network requests, live crawling, browser execution, response-body reads,
runtime mutation, automatic updates, or autonomous execution are performed here.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v19.89.8-S485-S491"
PHASE = "S485-S491"
JS_ASSET = "frontend/cockpit/shell/assets/claire_innovation_route_escalation.js"
CSS_ASSET = "frontend/cockpit/shell/assets/claire_innovation_route_escalation.css"


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
    "automatic_escalation_execution_enabled": False,
}


INNOVATION_SIGNAL_TERMS: Dict[str, List[str]] = {
    "market_gap": [
        "gap",
        "white space",
        "underserved",
        "unmet demand",
        "latent demand",
        "market pain",
        "customer pain",
        "category gap",
    ],
    "breakthrough": [
        "breakthrough",
        "novel",
        "new approach",
        "disruptive",
        "non-obvious",
        "invention",
        "invent",
        "category creation",
    ],
    "engineering": [
        "buildable",
        "architecture",
        "system design",
        "component",
        "dependency",
        "prototype",
        "manufacturable",
        "deployable",
        "feasible",
    ],
    "portfolio": [
        "portfolio",
        "allocation",
        "exposure",
        "rebalance",
        "optimization",
        "risk-adjusted",
        "thesis",
        "positioning",
    ],
    "acquisition": [
        "acquirer",
        "acquisition",
        "m&a",
        "strategic buyer",
        "exit",
        "package",
        "deal rationale",
        "strategic fit",
    ],
    "update_governance": [
        "update",
        "online update",
        "staged update",
        "rollback",
        "approval",
        "validation",
        "package validation",
    ],
    "recursive_learning": [
        "recursive",
        "self-ingestion",
        "learning loop",
        "memory loop",
        "longitudinal",
        "replay",
        "improve future runs",
    ],
}


ESCALATION_ROUTES: Dict[str, Dict[str, Any]] = {
    "portfolio_optimization": {
        "label": "Portfolio Optimization Route",
        "route_id": "portfolio_creation_or_optimization",
        "trigger_categories": ["portfolio", "market_gap"],
        "minimum_score": 0.42,
        "requires": ["trend_or_thesis_context", "risk_notes", "evidence_basket"],
    },
    "breakthrough_escalation": {
        "label": "Breakthrough Escalation Route",
        "route_id": "breakthrough_identification_and_classification",
        "trigger_categories": ["breakthrough", "market_gap", "engineering"],
        "minimum_score": 0.50,
        "requires": ["structural_gap", "non_obvious_advancement", "evidence_basket"],
    },
    "engineering_design": {
        "label": "Engineering / Design Route",
        "route_id": "auto_invention_solution_generation_to_design_portal",
        "trigger_categories": ["engineering", "breakthrough"],
        "minimum_score": 0.46,
        "requires": ["buildability_context", "dependencies", "constraints"],
    },
    "acquisition_package": {
        "label": "Acquisition Package Route",
        "route_id": "acquirer_identification_to_final_package",
        "trigger_categories": ["acquisition", "market_gap", "portfolio"],
        "minimum_score": 0.48,
        "requires": ["strategic_fit", "value_capture", "package_readiness"],
    },
    "update_governance": {
        "label": "Governed Update Readiness Route",
        "route_id": "online_update_readiness_to_staged_validation",
        "trigger_categories": ["update_governance"],
        "minimum_score": 0.44,
        "requires": ["zero_trust_scan", "rollback_plan", "operator_approval"],
    },
    "recursive_learning": {
        "label": "Recursive Learning Route",
        "route_id": "lifecycle_memory_and_recursive_self_ingestion",
        "trigger_categories": ["recursive_learning"],
        "minimum_score": 0.44,
        "requires": ["run_history", "evidence_trace", "replay_contract"],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: str | None) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


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


def _load_domain_routes_module():
    from claire.api import claire_domain_answer_routes_s478_s484 as domain_routes

    return domain_routes


def _load_kb_module():
    from claire.api import claire_knowledge_base_registry_s471_s477 as kb_registry

    return kb_registry


def _score_signal_categories(text: str, route_output: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
    normalized = _normalize(text)
    route_text = ""
    if route_output:
        route_text = _normalize(
            " ".join(
                [
                    str(route_output.get("route_selection", {})),
                    str(route_output.get("route_sections", {})),
                    str(route_output.get("knowledge_results", {})),
                    str(route_output.get("answer_quality_state", "")),
                ]
            )
        )
    haystack = f"{normalized} {route_text}".strip()

    scores: Dict[str, Dict[str, Any]] = {}
    for category, terms in INNOVATION_SIGNAL_TERMS.items():
        matched = [term for term in terms if term in haystack]
        raw = min(1.0, 0.18 * len(matched))
        if route_output:
            selected_route = route_output.get("route_selection", {}).get("selected_domain_route", "")
            if category == "engineering" and selected_route == "engineering":
                raw += 0.12
            if category in {"market_gap", "portfolio"} and selected_route == "market":
                raw += 0.10
            if selected_route == "cross_domain":
                raw += 0.06
        scores[category] = {
            "score": round(_clamp(raw), 3),
            "matched_terms": matched,
        }
    return scores


def _aggregate_innovation_score(category_scores: Dict[str, Dict[str, Any]], route_output: Optional[Dict[str, Any]] = None) -> float:
    scores = [value["score"] for value in category_scores.values()]
    top = sorted(scores, reverse=True)[:3]
    base = sum(top) / 3 if top else 0.0

    route_bonus = 0.0
    if route_output:
        evidence_answer = route_output.get("evidence_answer", {})
        confidence = _clamp(evidence_answer.get("confidence", route_output.get("confidence", 0.0)))
        if confidence >= 0.70:
            route_bonus += 0.08
        if evidence_answer.get("innovation_potential") is True:
            route_bonus += 0.10
        if route_output.get("answer_quality_state") == "evidence_backed":
            route_bonus += 0.04

    return round(_clamp(base + route_bonus), 3)


def _potential_level(score: float) -> str:
    if score >= 0.72:
        return "high"
    if score >= 0.50:
        return "qualified"
    if score >= 0.32:
        return "watch"
    return "low"


def _candidate_routes(category_scores: Dict[str, Dict[str, Any]], innovation_score: float) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for key, route in ESCALATION_ROUTES.items():
        route_category_scores = [
            category_scores.get(category, {}).get("score", 0.0)
            for category in route["trigger_categories"]
        ]
        category_score = max(route_category_scores) if route_category_scores else 0.0
        composite = round(_clamp((category_score * 0.70) + (innovation_score * 0.30)), 3)
        qualifies = composite >= float(route["minimum_score"])
        if qualifies or composite >= 0.30:
            candidates.append(
                {
                    "candidate_key": key,
                    "label": route["label"],
                    "route_id": route["route_id"],
                    "composite_score": composite,
                    "qualifies_for_review": qualifies,
                    "requires": route["requires"],
                    "trigger_categories": route["trigger_categories"],
                }
            )
    candidates.sort(key=lambda item: item["composite_score"], reverse=True)
    return candidates


def detect_innovation_potential(
    question: str | None,
    context: Optional[Dict[str, Any]] = None,
    preferred_domain: str | None = None,
) -> Dict[str, Any]:
    """Detect innovation potential and advisory route candidates without executing escalation."""
    domain_routes = _load_domain_routes_module()
    route_output = domain_routes.build_domain_answer_route(
        question,
        preferred_domain=preferred_domain,
        context=context or {},
    )

    category_scores = _score_signal_categories(question or "", route_output=route_output)
    innovation_score = _aggregate_innovation_score(category_scores, route_output=route_output)
    level = _potential_level(innovation_score)
    candidates = _candidate_routes(category_scores, innovation_score)

    requires_operator_review = level in {"qualified", "high"} or any(candidate["qualifies_for_review"] for candidate in candidates)
    selected_candidate = candidates[0] if candidates and candidates[0]["qualifies_for_review"] else None

    result = {
        "version": VERSION,
        "created_at": _now(),
        "question": str(question or ""),
        "route_output_summary": {
            "selected_domain_route": route_output["route_selection"]["selected_domain_route"],
            "route_id": route_output["route_selection"]["route_id"],
            "answer_quality_state": route_output.get("answer_quality_state"),
            "confidence": route_output.get("confidence"),
        },
        "category_scores": category_scores,
        "innovation_score": innovation_score,
        "innovation_potential_level": level,
        "route_candidates": candidates,
        "selected_candidate": selected_candidate,
        "requires_operator_review": requires_operator_review,
        "escalation_execution_allowed": False,
        "recommended_operator_action": (
            "review_candidate_route"
            if selected_candidate
            else "continue_evidence_collection_or_keep_as_watch_signal"
        ),
        "governance_note": "This detector recommends route review only. It does not execute escalation or mutate runtime truth.",
    }
    result.update(BLOCKED_AUTHORITY)
    return result


def build_s485_innovation_signal_schema() -> Dict[str, Any]:
    return _safe_base(
        "S485",
        "innovation_signal_schema_ready",
        categories=INNOVATION_SIGNAL_TERMS,
        signal_fields=[
            "category",
            "matched_terms",
            "category_score",
            "innovation_score",
            "innovation_potential_level",
            "route_candidates",
            "requires_operator_review",
        ],
        supported_levels=["low", "watch", "qualified", "high"],
    )


def build_s486_innovation_scoring_contract() -> Dict[str, Any]:
    sample = detect_innovation_potential(
        "Can Claire identify the market gap and buildable breakthrough route for this system design?"
    )
    return _safe_base(
        "S486",
        "innovation_scoring_contract_ready",
        scoring_rules=[
            "Matched category terms create category scores.",
            "Evidence-backed route confidence adds bounded bonus.",
            "Innovation potential from S450/S478 context adds bounded bonus.",
            "Scores create low/watch/qualified/high levels.",
            "Qualified/high recommendations require operator review and do not execute.",
        ],
        sample_score={
            "innovation_score": sample["innovation_score"],
            "innovation_potential_level": sample["innovation_potential_level"],
            "selected_candidate": sample["selected_candidate"],
        },
    )


def build_s487_route_escalation_contract() -> Dict[str, Any]:
    return _safe_base(
        "S487",
        "route_escalation_contract_ready",
        escalation_routes=ESCALATION_ROUTES,
        escalation_rules=[
            "Route candidates are advisory only.",
            "A qualifying candidate may be reviewed by the operator.",
            "Lifecycle runtime must own any actual route transition.",
            "No route candidate can mutate active runtime truth.",
            "No route candidate can trigger automatic updates or autonomous execution.",
        ],
    )


def build_breakthrough_candidate(question: str | None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    detection = detect_innovation_potential(question, context=context)
    category_scores = detection["category_scores"]
    breakthrough_score = max(
        category_scores.get("breakthrough", {}).get("score", 0.0),
        category_scores.get("market_gap", {}).get("score", 0.0),
        category_scores.get("engineering", {}).get("score", 0.0),
    )
    candidate = {
        "candidate_id": f"breakthrough_candidate_{abs(hash((question, detection['innovation_score']))) % 10_000_000:07d}",
        "question": str(question or ""),
        "breakthrough_score": round(_clamp((breakthrough_score * 0.65) + (detection["innovation_score"] * 0.35)), 3),
        "category_scores": {
            "breakthrough": category_scores.get("breakthrough", {}),
            "market_gap": category_scores.get("market_gap", {}),
            "engineering": category_scores.get("engineering", {}),
        },
        "classification": (
            "breakthrough_review_candidate"
            if detection["innovation_potential_level"] in {"qualified", "high"}
            else "not_yet_qualified"
        ),
        "route_review_required": detection["requires_operator_review"],
        "recommended_route_candidate": detection["selected_candidate"],
        "execution_allowed": False,
    }
    candidate.update(BLOCKED_AUTHORITY)
    return candidate


def build_s488_breakthrough_candidate_contract() -> Dict[str, Any]:
    sample = build_breakthrough_candidate(
        "Can Claire find a non-obvious breakthrough and buildable system design from this market gap?"
    )
    return _safe_base(
        "S488",
        "breakthrough_candidate_contract_ready",
        candidate_fields=[
            "candidate_id",
            "question",
            "breakthrough_score",
            "category_scores",
            "classification",
            "route_review_required",
            "recommended_route_candidate",
            "execution_allowed",
        ],
        sample_candidate=sample,
    )


def build_s489_escalation_guardrail_contract() -> Dict[str, Any]:
    return _safe_base(
        "S489",
        "escalation_guardrail_contract_ready",
        blocked_escalation_authority=[
            "execute_route_transition",
            "write_runtime_truth",
            "mutate_active_runtime",
            "apply_online_update",
            "start_autonomous_crawler",
            "perform_live_web_execution",
            "read_response_body_without_governed_fetch",
        ],
        allowed_escalation_outputs=[
            "candidate_route",
            "operator_review_required",
            "evidence_requirement",
            "route_review_packet",
            "safe_next_operator_action",
        ],
        guardrail_rules=[
            "Escalation detection is not escalation execution.",
            "Operator review is required for qualified/high route candidates.",
            "Lifecycle runtime must validate any actual transition.",
            "Governance documents override speed and convenience.",
        ],
    )


def build_s490_cockpit_asset_manifest(project_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(project_root) if project_root is not None else Path.cwd()
    js = root / JS_ASSET
    css = root / CSS_ASSET
    return _safe_base(
        "S490",
        "cockpit_asset_manifest_ready",
        assets={
            "js": JS_ASSET,
            "css": CSS_ASSET,
            "js_exists": js.exists(),
            "css_exists": css.exists(),
        },
        cockpit_regions=[
            "innovation_potential_panel",
            "category_score_cards",
            "route_candidate_cards",
            "operator_review_required_badge",
            "escalation_guardrail_footer",
        ],
        visual_authority="presentation_only",
    )


def build_s491_stop_gate(report_dir: str | Path | None = None, project_root: str | Path | None = None) -> Dict[str, Any]:
    s485 = build_s485_innovation_signal_schema()
    s486 = build_s486_innovation_scoring_contract()
    s487 = build_s487_route_escalation_contract()
    s488 = build_s488_breakthrough_candidate_contract()
    s489 = build_s489_escalation_guardrail_contract()
    s490 = build_s490_cockpit_asset_manifest(project_root)

    market_detection = detect_innovation_potential(
        "Can Claire find a market gap and portfolio optimization route from this trend?",
        preferred_domain="market",
    )
    engineering_detection = detect_innovation_potential(
        "Can Claire identify a buildable breakthrough system design with feasible architecture?",
        preferred_domain="engineering",
    )
    update_detection = detect_innovation_potential(
        "Can Claire evaluate an online update package with rollback validation and approval?",
    )
    breakthrough_candidate = build_breakthrough_candidate(
        "Can Claire find a non-obvious breakthrough from this market gap and system design?"
    )

    checks = {
        "s485_schema_ready": "breakthrough" in s485["categories"],
        "s486_scoring_ready": s486["sample_score"]["innovation_potential_level"] in {"low", "watch", "qualified", "high"},
        "s487_routes_ready": "breakthrough_escalation" in s487["escalation_routes"],
        "s488_candidate_ready": s488["sample_candidate"]["execution_allowed"] is False,
        "s489_guardrails_ready": "write_runtime_truth" in s489["blocked_escalation_authority"],
        "s490_assets_exist": s490["assets"]["js_exists"] is True and s490["assets"]["css_exists"] is True,
        "market_detection_safe": all(market_detection.get(flag) is False for flag in BLOCKED_AUTHORITY),
        "engineering_detection_has_candidate": len(engineering_detection["route_candidates"]) >= 1,
        "update_detection_finds_update_route": any(candidate["candidate_key"] == "update_governance" for candidate in update_detection["route_candidates"]),
        "breakthrough_candidate_safe": breakthrough_candidate["execution_allowed"] is False and all(breakthrough_candidate.get(flag) is False for flag in BLOCKED_AUTHORITY),
    }

    ok = all(checks.values())
    result = _safe_base(
        "S491",
        "claire_innovation_route_escalation_passed" if ok else "claire_innovation_route_escalation_failed",
        ok=ok,
        ready=ok,
        checks=checks,
        sample_outputs={
            "market_detection": market_detection,
            "engineering_detection": engineering_detection,
            "update_detection": update_detection,
            "breakthrough_candidate": breakthrough_candidate,
        },
        forward_motion_allowed=ok,
        next_phase="S492-S498 Useful output package preview",
    )

    if report_dir is not None:
        target_dir = Path(report_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "s491_claire_innovation_route_escalation_stop_gate.json").write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )

    return result


def build_claire_innovation_route_escalation_s485_s491(project_root: str | Path | None = None) -> Dict[str, Any]:
    return _safe_base(
        "S485-S491",
        "claire_innovation_route_escalation_ready",
        contracts={
            "s485": build_s485_innovation_signal_schema(),
            "s486": build_s486_innovation_scoring_contract(),
            "s487": build_s487_route_escalation_contract(),
            "s488": build_s488_breakthrough_candidate_contract(),
            "s489": build_s489_escalation_guardrail_contract(),
            "s490": build_s490_cockpit_asset_manifest(project_root),
        },
        stop_gate=build_s491_stop_gate(project_root=project_root),
    )


__all__ = [
    "VERSION",
    "PHASE",
    "BLOCKED_AUTHORITY",
    "INNOVATION_SIGNAL_TERMS",
    "ESCALATION_ROUTES",
    "detect_innovation_potential",
    "build_breakthrough_candidate",
    "build_s485_innovation_signal_schema",
    "build_s486_innovation_scoring_contract",
    "build_s487_route_escalation_contract",
    "build_s488_breakthrough_candidate_contract",
    "build_s489_escalation_guardrail_contract",
    "build_s490_cockpit_asset_manifest",
    "build_s491_stop_gate",
    "build_claire_innovation_route_escalation_s485_s491",
]
