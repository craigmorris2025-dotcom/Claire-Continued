from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from runtime_core.strategic_world.governance import GovernanceContext, GovernanceGuard
from runtime_core.strategic_world.objectives import MultiStakeholderCoordinator, StrategicWorldOption


SCHEMA_VERSION = "claire.strategic_world.layer.v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text_terms(*values: Any) -> list[str]:
    stop = {"and", "the", "for", "with", "from", "into", "this", "that", "because", "should", "could"}
    counts: Counter[str] = Counter()

    def walk(value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(walk(item) for item in value.values())
        if isinstance(value, list):
            return " ".join(walk(item) for item in value)
        return str(value or "")

    for value in values:
        for raw in walk(value).lower().replace("_", " ").replace("-", " ").replace("/", " ").split():
            token = "".join(ch for ch in raw if ch.isalnum())
            if len(token) >= 4 and token not in stop:
                counts[token] += 1
    return [term for term, _ in counts.most_common(16)]


def _infer_domains(keywords: list[str], route: str) -> list[str]:
    joined = " ".join(keywords)
    domains: list[str] = []
    if any(term in joined for term in ("technology", "software", "platform", "system", "architecture", "autonomous", "invention")):
        domains.append("technology")
    if any(term in joined for term in ("market", "portfolio", "buyer", "acquisition", "revenue")):
        domains.append("market")
    if any(term in joined for term in ("governance", "compliance", "regulatory", "risk")):
        domains.append("governance")
    if "existing_system_replacement" in route:
        domains.append("systems")
    return list(dict.fromkeys(domains or ["market_intelligence"]))


def _meta_policy(emergence: dict[str, Any], memory_records: list[dict[str, Any]]) -> dict[str, Any]:
    route_counts: Counter[str] = Counter()
    pattern_counts: Counter[str] = Counter()
    for record in memory_records:
        result = _as_dict(record.get("result"))
        route_counts[str(result.get("route_selected") or "unknown")] += 1
        for pattern in _as_list(_as_dict(result.get("emergence_engine")).get("detected_patterns")):
            pattern_id = pattern.get("pattern_id") if isinstance(pattern, dict) else pattern
            if pattern_id:
                pattern_counts[str(pattern_id)] += 1
    detected = [
        str(item.get("pattern_id"))
        for item in _as_list(emergence.get("detected_patterns"))
        if isinstance(item, dict) and item.get("pattern_id")
    ]
    weights = {
        pattern_id: round(1.0 + min(0.35, pattern_counts.get(pattern_id, 0) / 100), 4)
        for pattern_id in detected
    }
    dominant_route = route_counts.most_common(1)[0][0] if route_counts else None
    return {
        "status": "active" if memory_records else "waiting_for_lived_cycles",
        "memory_run_count": len(memory_records),
        "dominant_memory_route": dominant_route,
        "pattern_weight_overrides": weights,
        "confidence_calibration": {
            "policy": "conservative_until_labeled_outcomes",
            "high": -0.05 if len(memory_records) < 50 else 0.0,
            "mid": -0.025 if len(memory_records) < 50 else 0.0,
        },
        "runtime_truth_mutation_allowed": False,
    }


def _world_snapshot(run_spine: dict[str, Any], keywords: list[str], domains: list[str]) -> dict[str, Any]:
    emergence = _as_dict(run_spine.get("emergence_engine"))
    patterns = [
        item for item in _as_list(emergence.get("detected_patterns"))
        if isinstance(item, dict)
    ]
    themes = [
        str(item.get("name") or item.get("pattern_id"))
        for item in patterns
        if item.get("name") or item.get("pattern_id")
    ]
    route = str(run_spine.get("route_selected") or "unknown")
    if route == "existing_system_replacement":
        themes.append("existing system replacement")
    if _as_dict(run_spine.get("evidence_governance")).get("status"):
        themes.append("governed evidence routing")
    risks = []
    if not _as_list(run_spine.get("signals")):
        risks.append("insufficient fresh evidence")
    if route == "existing_system_replacement":
        risks.append("replacement design needs operator review before promotion")
    if not _as_dict(run_spine.get("quality_gate")).get("design_proof_complete"):
        risks.append("design proof incomplete or route skipped")
    opportunities = [
        "convert detected pattern into review-ready portfolio package",
        "attach current market and buyer evidence before external claims",
    ]
    if route == "existing_system_replacement":
        opportunities.append("turn system decomposition into superior replacement design package")
    return {
        "timestamp": _now(),
        "domains": [
            {
                "domain": domain,
                "active_themes": themes[:6],
                "keyword_basis": keywords[:8],
                "route_selected": route,
            }
            for domain in domains
        ],
        "cross_domain_themes": list(dict.fromkeys(themes))[:10],
        "systemic_risks": risks,
        "systemic_opportunities": opportunities,
    }


def _options(route: str, domains: list[str], run_spine: dict[str, Any]) -> list[StrategicWorldOption]:
    evidence_present = bool(_as_list(run_spine.get("signals")))
    design_selected = bool(_as_dict(run_spine.get("design_candidate")))
    return [
        StrategicWorldOption(
            id="continue_governed_evidence_collection",
            label="Continue governed evidence collection",
            description="Strengthen the claim base before promotion, market valuation, or public claims.",
            affected_domains=domains,
            expected_impacts={"evidence": 0.35, "risk_reduction": 0.28, "reversibility": 0.30, "readiness": 0.12, "value_capture": 0.08},
            risk_class="low",
        ),
        StrategicWorldOption(
            id="prepare_design_portal_review",
            label="Prepare Design Portal review",
            description="Move qualified solution or replacement design into operator-reviewed blueprint, material, and feasibility checks.",
            affected_domains=domains,
            expected_impacts={"readiness": 0.32 if design_selected or route == "existing_system_replacement" else 0.12, "evidence": 0.18, "risk_reduction": 0.24, "reversibility": 0.18, "value_capture": 0.22},
            risk_class="medium",
        ),
        StrategicWorldOption(
            id="run_acquirer_diligence_package",
            label="Run acquirer diligence package",
            description="Convert strategic acquirer matches into a review-ready capability-gap and buyer-fit memo.",
            affected_domains=["market", *domains],
            expected_impacts={"readiness": 0.24, "evidence": 0.20 if evidence_present else 0.10, "risk_reduction": 0.12, "reversibility": 0.20, "value_capture": 0.34},
            risk_class="medium",
        ),
    ]


def build_strategic_world_layer(
    run_spine: dict[str, Any],
    *,
    memory_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    memory_records = memory_records or []
    route = str(run_spine.get("route_selected") or "unknown")
    keywords = _text_terms(run_spine.get("trend"), run_spine.get("thesis"), run_spine.get("portfolio_candidate"), run_spine.get("signals"))
    domains = _infer_domains(keywords, route)
    emergence = _as_dict(run_spine.get("emergence_engine"))
    snapshot = _world_snapshot(run_spine, keywords, domains)
    options = _options(route, domains, run_spine)
    recommendations = MultiStakeholderCoordinator().evaluate(options)
    top = recommendations[0] if recommendations else None
    top_option = next((option for option in options if top and option.id == top.option_id), None)
    guard = GovernanceGuard()
    governance_decision = guard.evaluate(
        GovernanceContext(
            actor_role_id="runtime",
            action="propose_intervention",
            risk_class=(top_option.risk_class if top_option else "low"),  # type: ignore[arg-type]
            objective_summary=(top_option.description if top_option else "No strategic-world option selected."),
        )
    )
    blocked_execution = guard.evaluate(
        GovernanceContext(
            actor_role_id="runtime",
            action="execute_external_action",
            risk_class="unbounded",
            objective_summary="External action from strategic world layer.",
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "strategic_world_ready",
        "generated_at": _now(),
        "route_selected": route,
        "domains": domains,
        "keyword_basis": keywords,
        "meta_emergence_policy": _meta_policy(emergence, memory_records),
        "world_snapshot": snapshot,
        "options": [
            {
                "id": option.id,
                "label": option.label,
                "description": option.description,
                "affected_domains": option.affected_domains,
                "expected_impacts": option.expected_impacts,
                "risk_class": option.risk_class,
                "execution_boundary": option.execution_boundary,
            }
            for option in options
        ],
        "ranked_recommendations": [
            {
                "option_id": item.option_id,
                "score": item.score,
                "per_stakeholder_scores": item.per_stakeholder_scores,
            }
            for item in recommendations
        ],
        "governance": {
            "proposal_allowed": governance_decision.allowed,
            "proposal_reason": governance_decision.reason,
            "requires_human_approval": governance_decision.requires_human_approval,
            "external_execution_allowed": blocked_execution.allowed,
            "external_execution_reason": blocked_execution.reason,
            "execution_boundary": "recommendation_only_no_external_action_without_operator_approval",
        },
        "authority": {
            "network_request_performed": False,
            "external_action_performed": False,
            "runtime_truth_mutated": False,
            "automatic_update_performed": False,
            "operator_review_required": True,
        },
    }
