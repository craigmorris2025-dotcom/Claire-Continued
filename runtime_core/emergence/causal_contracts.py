from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from runtime_core.lifecycle.canonical_paths import (
    ACQUISITION_ROUTE,
    BREAKTHROUGH_DESIGN_ROUTE,
    BREAKTHROUGH_ESCALATION_ROUTE,
    EXISTING_SYSTEM_REPLACEMENT_ROUTE,
    PORTFOLIO_ROUTE,
)


SCHEMA_VERSION = "claire.emergence.causal_contracts.v1"
GLOBAL_SIMILARITY_THRESHOLD = 0.65
ROUTE_ANALOG_THRESHOLD = 0.60
MOMENTUM_THRESHOLD = 0.55

SOURCE_FILES = [
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/Causal Schemas.txt",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.causal_bubble_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.causal_runtime.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.causal_timeline_engine.(patched core).py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.causal_timeline_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.coordinated_intervention_orchestrator.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.emergence.meta_emergence_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.emergence.strategy_council.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.emergence_reasoning_runtime.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.enabling_condition_detector.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.global_emergence_matcher.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.global_similarity_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.governance.governance_guard.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.governancecharter.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.historical_bubble_ingestion.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.historical_similarity_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.recursive_memory.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.route_selector.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.timeline_reconstruction_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.unified_causal_engine.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.world.coordinated_intervention_orchestrator.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.world.emergence_world_map.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/claire.world.multi_stakeholder_objectives.py",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/lock conditions.txt",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/solved condition logic.txt",
    "C:/Users/craig/OneDrive/Desktop/Claire emergence/THE UNIFIED LOOP.txt",
]


FEATURE_SCHEMA = {
    "sociocultural": [
        "cultural_shift",
        "lifestyle_change",
        "trust_in_institutions",
        "privacy_concern",
        "labor_market_pressure",
        "adoption_readiness",
    ],
    "economic": [
        "cost_pressure",
        "consumer_power",
        "enterprise_budget",
        "supply_chain_stability",
        "macro_cycle",
        "capital_inflow",
    ],
    "market": [
        "unmet_demand",
        "incumbent_stagnation",
        "pricing_inefficiency",
        "distribution_bottlenecks",
        "competitive_gap",
        "market_fragmentation",
    ],
    "technological": [
        "performance_level",
        "cost_collapse",
        "infra_maturity",
        "scientific_readiness",
        "manufacturability",
        "novelty",
        "structural_shift",
    ],
    "regulatory": ["friction", "openness", "subsidies", "compliance_burden", "policy_pressure"],
    "geopolitical": [
        "supply_chain_risk",
        "energy_dependency",
        "national_security_pressure",
        "global_competition",
        "instability",
    ],
    "enabling": [
        "cost_collapse",
        "performance_breakthrough",
        "infrastructure_maturity",
        "demand_pressure",
        "regulatory_opening",
        "capital_flow",
        "cultural_shift",
    ],
    "timeline": ["event_density", "acceleration_rate", "time_to_breakthrough"],
}


@dataclass
class TimelineEvent:
    event_date: str
    event: str
    signal_changes: dict[str, float] = field(default_factory=dict)
    enabling_condition: str | None = None


@dataclass
class CausalTimeline:
    root_pressure: str = ""
    system_failure: str = ""
    enabling_conditions: list[str] = field(default_factory=list)
    breakthrough_trigger: str = ""
    global_accelerants: list[str] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)


def _score(value: Any, default: float = 0.0) -> float:
    try:
        return round(max(0.0, min(1.0, float(value))), 4)
    except (TypeError, ValueError):
        return default


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _first_score(payload: dict[str, Any], paths: list[tuple[str, ...]], default: float = 0.0) -> float:
    for path in paths:
        value = _nested(payload, *path)
        if value is not None and value != "":
            return _score(value, default)
    return default


def build_causal_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "source_file_count": len(SOURCE_FILES),
        "source_files": SOURCE_FILES,
        "feature_schema": FEATURE_SCHEMA,
        "canonical_models": {
            "CausalTimeline": [field.name for field in CausalTimeline.__dataclass_fields__.values()],
            "TimelineEvent": [field.name for field in TimelineEvent.__dataclass_fields__.values()],
            "CausalBubble": [
                "sociocultural",
                "economic",
                "market",
                "technological",
                "regulatory",
                "geopolitical",
                "actors",
                "timeline",
                "enabling_conditions",
                "root_pressures",
                "system_failures",
                "breakthrough_trigger",
            ],
        },
        "thresholds": {
            "global_similarity": GLOBAL_SIMILARITY_THRESHOLD,
            "route_analog": ROUTE_ANALOG_THRESHOLD,
            "momentum": MOMENTUM_THRESHOLD,
        },
        "unified_loop": [
            "ingest_live_signals",
            "build_causal_bubble",
            "reconstruct_causal_timeline",
            "detect_enabling_conditions",
            "compute_momentum",
            "compare_to_historical_bubbles",
            "identify_causal_analogs",
            "predict_emergence",
            "select_route_vector",
            "generate_output",
            "store_bubble_and_output",
            "refine_thresholds_patterns_and_causal_logic",
            "repeat",
        ],
        "authority": {
            "backend_owns_truth": True,
            "runtime_truth_mutation": False,
            "route_truth_mutation": False,
            "dashboard_may_render_only": True,
            "operator_review_required": True,
            "autonomous_intervention_allowed": False,
        },
    }


def _extract_scores(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "demand_pressure": _first_score(payload, [("enabling", "demand_pressure"), ("market", "unmet_demand"), ("features", "unmet_need"), ("features", "demand_pressure")]),
        "cost_collapse": _first_score(payload, [("enabling", "cost_collapse"), ("technological", "cost_collapse"), ("features", "cost_trend_down"), ("features", "cost_collapse")]),
        "performance_breakthrough": _first_score(payload, [("enabling", "performance_breakthrough"), ("technological", "performance_level"), ("features", "perf_above_threshold"), ("features", "performance_breakthrough")]),
        "infrastructure_maturity": _first_score(payload, [("enabling", "infrastructure_maturity"), ("technological", "infra_maturity"), ("features", "infra_coverage")]),
        "regulatory_opening": _first_score(payload, [("enabling", "regulatory_opening"), ("regulatory", "openness"), ("features", "regulatory_friction_drop")]),
        "capital_flow": _first_score(payload, [("enabling", "capital_flow"), ("economic", "capital_inflow"), ("features", "capital_inflow")]),
        "cultural_shift": _first_score(payload, [("enabling", "cultural_shift"), ("sociocultural", "cultural_shift"), ("features", "cultural_readiness")]),
        "competitive_gap": _first_score(payload, [("market", "competitive_gap"), ("features", "competitive_gap")]),
        "manufacturability": _first_score(payload, [("technological", "manufacturability"), ("features", "manufacturability")]),
        "scientific_readiness": _first_score(payload, [("technological", "scientific_readiness"), ("features", "scientific_readiness")]),
    }


def _momentum(scores: dict[str, Any]) -> float:
    return _score(
        0.20 * scores["cost_collapse"]
        + 0.20 * scores["performance_breakthrough"]
        + 0.15 * scores["infrastructure_maturity"]
        + 0.15 * scores["demand_pressure"]
        + 0.10 * scores["regulatory_opening"]
        + 0.10 * scores["capital_flow"]
        + 0.10 * scores["cultural_shift"]
    )


def _similarity(payload: dict[str, Any]) -> float:
    explicit = payload.get("similarity")
    if explicit is not None:
        return _score(explicit)
    matches = _list(payload.get("historical_matches"))
    return _score(max((_score(_dict(match).get("similarity")) for match in matches), default=0.0))


def _stage_ready(payload: dict[str, Any]) -> bool:
    readiness = _dict(payload.get("stage_readiness"))
    return all(
        readiness.get(key) is True
        for key in ("trend_discovery_complete", "discovery_complete", "breakthrough_complete")
    )


def _causal_timeline(payload: dict[str, Any]) -> dict[str, Any]:
    timeline = _dict(payload.get("causal_timeline"))
    events = []
    for item in _list(timeline.get("timeline") or payload.get("timeline")):
        if not isinstance(item, dict):
            continue
        events.append(
            asdict(
                TimelineEvent(
                    event_date=str(item.get("date") or item.get("event_date") or date.today().isoformat()),
                    event=str(item.get("event") or ""),
                    signal_changes={str(k): _score(v) for k, v in _dict(item.get("signal_changes")).items()},
                    enabling_condition=item.get("enabling_condition"),
                )
            )
        )
    return asdict(
        CausalTimeline(
            root_pressure=str(timeline.get("root_pressure") or payload.get("root_pressure") or ""),
            system_failure=str(timeline.get("system_failure") or payload.get("system_failure") or ""),
            enabling_conditions=[str(item) for item in _list(timeline.get("enabling_conditions") or payload.get("enabling_conditions"))],
            breakthrough_trigger=str(timeline.get("breakthrough_trigger") or payload.get("breakthrough_trigger") or ""),
            global_accelerants=[str(item) for item in _list(timeline.get("global_accelerants") or payload.get("global_accelerants"))],
            timeline=[TimelineEvent(**event) for event in events],
        )
    )


def assess_causal_emergence(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    scores = _extract_scores(payload)
    momentum = _momentum(scores)
    similarity = _similarity(payload)
    breakthrough_trigger = str(payload.get("breakthrough_trigger") or _nested(payload, "bubble", "breakthrough_trigger") or "")
    system_failures = _list(payload.get("system_failures") or _nested(payload, "bubble", "system_failures"))

    evidence_present = any(value > 0 for value in scores.values()) or similarity > 0 or bool(system_failures)
    if not evidence_present:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "insufficient_data",
            "route_selected": "insufficient_data",
            "route_vector": [],
            "reason": "no causal scores, historical similarity, or system failures were provided",
            "authority": build_causal_contract()["authority"],
        }

    route_vector: list[dict[str, Any]] = []

    if scores["demand_pressure"] >= 0.40 and momentum < MOMENTUM_THRESHOLD:
        route_vector.append({"route_id": "portfolio", "route": PORTFOLIO_ROUTE, "score": scores["demand_pressure"], "reason": "market demand with sub-breakthrough momentum"})

    if (
        momentum >= MOMENTUM_THRESHOLD
        and scores["performance_breakthrough"] >= 0.50
        and scores["cost_collapse"] >= 0.40
    ):
        route_vector.append({"route_id": "breakthrough", "route": BREAKTHROUGH_ESCALATION_ROUTE, "score": momentum, "reason": "enabling momentum and performance threshold are active"})

    design_ready = (
        breakthrough_trigger == "technological"
        and scores["manufacturability"] >= 0.50
        and scores["scientific_readiness"] >= 0.50
    )
    if design_ready and _stage_ready(payload):
        route_vector.append({"route_id": "tech_design_build", "route": BREAKTHROUGH_DESIGN_ROUTE, "score": min(scores["manufacturability"], scores["scientific_readiness"]), "reason": "technological breakthrough is buildable after trend/discovery/breakthrough readiness"})
    elif design_ready:
        route_vector.append({"route_id": "tech_design_build_blocked", "route": PORTFOLIO_ROUTE, "score": min(scores["manufacturability"], scores["scientific_readiness"]), "reason": "design/CAD route blocked until trend -> discovery -> breakthrough are complete", "blocked": True})

    if scores["competitive_gap"] >= 0.50 and scores["capital_flow"] >= 0.50 and similarity >= ROUTE_ANALOG_THRESHOLD:
        route_vector.append({"route_id": "acquisition", "route": ACQUISITION_ROUTE, "score": min(scores["competitive_gap"], scores["capital_flow"], similarity), "reason": "strategic gap, capital flow, and acquisition analog are aligned"})

    if system_failures and momentum >= MOMENTUM_THRESHOLD and similarity >= ROUTE_ANALOG_THRESHOLD:
        route_vector.append({"route_id": "system_replacement", "route": EXISTING_SYSTEM_REPLACEMENT_ROUTE, "score": min(momentum, similarity), "reason": "old-system failure plus strong replacement analog"})

    active_routes = [item for item in route_vector if not item.get("blocked")]
    if not active_routes:
        active_routes = [{"route_id": "portfolio", "route": PORTFOLIO_ROUTE, "score": scores["demand_pressure"], "reason": "default bounded portfolio/discovery route"}]

    selected = active_routes[0]
    if len(active_routes) > 1:
        selected = {"route_id": "route_vector", "route": "route_vector", "score": max(item["score"] for item in active_routes), "reason": "multiple valid routes require governed operator review"}

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "route_selected": selected["route"],
        "route_selected_id": selected["route_id"],
        "route_vector": route_vector,
        "active_route_count": len(active_routes),
        "momentum": momentum,
        "similarity": similarity,
        "is_emerging": momentum >= MOMENTUM_THRESHOLD or similarity >= GLOBAL_SIMILARITY_THRESHOLD,
        "scores": scores,
        "causal_timeline": _causal_timeline(payload),
        "source_file_count": len(SOURCE_FILES),
        "authority": build_causal_contract()["authority"],
    }


__all__ = [
    "GLOBAL_SIMILARITY_THRESHOLD",
    "ROUTE_ANALOG_THRESHOLD",
    "SCHEMA_VERSION",
    "SOURCE_FILES",
    "assess_causal_emergence",
    "build_causal_contract",
]
