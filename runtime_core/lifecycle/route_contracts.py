from __future__ import annotations

from typing import Any

from .canonical_paths import (
    ACQUISITION_ROUTE,
    BREAKTHROUGH_DESIGN_ROUTE,
    BREAKTHROUGH_ESCALATION_ROUTE,
    EXISTING_SYSTEM_REPLACEMENT_ROUTE,
    PORTFOLIO_ROUTE,
)


SCHEMA_VERSION = "claire.lifecycle.route_contracts.v1"

TECH_DESIGN_BUILD_ROUTE_ID = "tech_design_build"
RECURSIVE_MEMORY_ROUTE_ID = "recursive_memory"

MARKET_FAMILY = {
    "market",
    "market_family",
    "portfolio",
    "portfolio_family",
    "consumer",
    "commerce",
    "media",
    "distribution",
    "behavior",
}

ACQUISITION_FAMILY = {
    "acquisition",
    "acquirer",
    "acquirer_fit",
    "buyer",
    "deal",
    "m_and_a",
    "moat",
    "strategic_value",
    "value_capture",
}

TECH_FAMILY = {
    "technology",
    "tech",
    "technical",
    "ai_native",
    "technology_catch_up",
    "infrastructure_catch_up",
    "ecosystem_lock_in",
    "verticalization",
    "buildable_now",
    "design_build",
    "hardware",
    "software",
    "system_design",
}

SYSTEM_REPLACEMENT_FAMILY = {
    "system_replacement",
    "existing_system_replacement",
    "replacement",
    "superior_system_design",
}


SOURCE_FILES = {
    "center": "C:/Users/craig/OneDrive/Desktop/routes/THE CENTER ROUTE CONTRACT.txt",
    "portfolio": "C:/Users/craig/OneDrive/Desktop/routes/ROUTE 1 — PORTFOLIO ROUTE.txt",
    "breakthrough": "C:/Users/craig/OneDrive/Desktop/routes/ROUTE 2 — BREAKTHROUGH ROUTE.txt",
    "tech_design_build": "C:/Users/craig/OneDrive/Desktop/routes/ROUTE 3 — TECH DESIGN  BUILD ROUTE.txt",
    "acquisition": "C:/Users/craig/OneDrive/Desktop/routes/ROUTE 4 — ACQUISITION ROUTE.txt",
    "recursive_memory": "C:/Users/craig/OneDrive/Desktop/routes/ROUTE 5 — RECURSIVE MEMORY ROUTE.txt",
}


def _normalize_family(value: Any) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .replace("&", "and")
        .replace("/", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )


def _nested(payload: Any, path: str) -> Any:
    current = payload
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _first_value(payload: dict[str, Any], paths: list[str]) -> Any:
    for path in paths:
        value = _nested(payload, path)
        if value is not None and value != "":
            return value
    return None


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _pass_min(value: float | None, threshold: float) -> bool | None:
    if value is None:
        return None
    return value >= threshold


def _pass_max(value: float | None, threshold: float) -> bool | None:
    if value is None:
        return None
    return value <= threshold


def _gate_status(checks: list[dict[str, Any]]) -> str:
    if any(item["passed"] is False for item in checks):
        return "failed"
    if any(item["passed"] is None for item in checks):
        return "not_evaluated"
    return "passed"


def _extract_breakthrough(outputs: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [
        outputs.get("breakthrough"),
        outputs.get("breakthrough_synthesis"),
        _nested(outputs, "core_output.breakthrough"),
        _nested(outputs, "core_output.breakthrough_synthesis"),
    ]
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate:
            return candidate
    if _first_value(outputs, ["scores.breakthrough_threshold", "scores.breakthrough_score", "scores.breakthrough_signal"]):
        return {"source": "scores"}
    return None


def _breakthrough_primary(outputs: dict[str, Any], breakthrough: dict[str, Any] | None) -> str:
    data = breakthrough or {}
    return _normalize_family(
        _first_value(
            data,
            [
                "primary",
                "primary_family",
                "primary_type",
                "primary_breakthrough_type",
                "route_family",
                "breakthrough_classification.primary",
                "breakthrough_classification.primary_type",
            ],
        )
        or _first_value(outputs, ["scores.breakthrough_primary", "thesis_formation.breakthrough_primary"])
    )


def _breakthrough_threshold(outputs: dict[str, Any], breakthrough: dict[str, Any] | None) -> float | None:
    data = breakthrough or {}
    return _float_or_none(
        _first_value(
            data,
            ["breakthrough_threshold", "threshold", "score", "readiness_score", "confidence"],
        )
        or _first_value(
            outputs,
            [
                "scores.breakthrough_threshold",
                "scores.breakthrough_score",
                "scores.breakthrough_signal",
                "breakthrough_threshold",
            ],
        )
    )


def _family_contains(primary: str, family: set[str]) -> bool:
    if primary in family:
        return True
    return any(primary.startswith(item + "_") or primary.endswith("_" + item) for item in family)


def build_center_route_contract() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "source_file": SOURCE_FILES["center"],
        "logic": [
            {"if": "breakthrough is None", "route": PORTFOLIO_ROUTE},
            {"if": "breakthrough_threshold < 0.55", "route": PORTFOLIO_ROUTE},
            {"if": "breakthrough.primary in MARKET_FAMILY", "route": PORTFOLIO_ROUTE},
            {"if": "breakthrough.primary in ACQUISITION_FAMILY", "route": ACQUISITION_ROUTE},
            {"if": "breakthrough.primary in TECH_FAMILY", "route": BREAKTHROUGH_DESIGN_ROUTE, "route_id": TECH_DESIGN_BUILD_ROUTE_ID},
            {"if": "breakthrough.primary == SYSTEM_REPLACEMENT", "route": EXISTING_SYSTEM_REPLACEMENT_ROUTE},
            {"else": "route", "route": BREAKTHROUGH_ESCALATION_ROUTE},
        ],
        "families": {
            "market": sorted(MARKET_FAMILY),
            "acquisition": sorted(ACQUISITION_FAMILY),
            "tech": sorted(TECH_FAMILY),
            "system_replacement": sorted(SYSTEM_REPLACEMENT_FAMILY),
        },
        "authority": {
            "backend_owns_route_truth": True,
            "dashboard_may_render_only": True,
            "manual_promotion_required": True,
            "runtime_truth_mutation": False,
        },
    }


def build_route_contracts() -> dict[str, Any]:
    contracts = {
        "portfolio": {
            "route": PORTFOLIO_ROUTE,
            "source_file": SOURCE_FILES["portfolio"],
            "center_section": "Stages 23 -> 26 -> 27",
            "what": "Portfolio action, optimization, positioning",
            "why": "Market evidence impacts portfolio structure",
            "when": "Market/thesis relevance passes thresholds",
            "trigger_source": ["trend", "market", "portfolio signal families"],
            "required_scores": {
                "trend_strength": {">=": 0.45},
                "thesis_quality": {">=": 0.50},
                "portfolio_relevance": {">=": 0.40},
                "risk_exposure": {"<=": 0.65},
            },
            "sequence": [23, 26, 27],
            "output": "Portfolio artifact with portfolio thesis, positioning, and risk map",
            "failure_state": "Generic/easy output; fallback portfolio",
        },
        "breakthrough": {
            "route": BREAKTHROUGH_ESCALATION_ROUTE,
            "source_file": SOURCE_FILES["breakthrough"],
            "center_section": "Stages 11 -> 12 -> 13 -> 14 -> 15",
            "what": "Escalation to breakthrough classification",
            "why": "Discovery exceeds normal market route",
            "when": "Gap + discovery + breakthrough threshold pass",
            "trigger_source": ["discovery", "gap", "breakthrough signal families"],
            "required_scores": {
                "gap_validity": {">=": 0.50},
                "gap_severity": {">=": 0.55},
                "breakthrough_threshold": {">=": 0.60},
            },
            "sequence": [11, 12, 13, 14, 15],
            "output": "Breakthrough classification object",
            "failure_state": "Strong signal stays portfolio-only; no escalation",
        },
        TECH_DESIGN_BUILD_ROUTE_ID: {
            "route": BREAKTHROUGH_DESIGN_ROUTE,
            "source_file": SOURCE_FILES["tech_design_build"],
            "center_section": "Stages 15 -> 16 -> 17 -> 18 -> 19 -> 20 -> 21 -> 22",
            "what": "Buildable-now design route from invention to feasibility",
            "why": "Tech breakthrough requires construction path",
            "when": "Breakthrough + innovation + buildability conditions pass",
            "trigger_source": ["breakthrough classification", "innovation path"],
            "required_scores": {
                "technology_signal": {">=": 0.55},
                "breakthrough_threshold": {">=": 0.60},
                "buildability_readiness": {">=": 0.50},
                "design_route_readiness": {">=": 0.50},
            },
            "sequence": [15, 16, 17, 18, 19, 20, 21, 22],
            "output": "Design portal contract, CAD intent, blueprint package",
            "failure_state": "Design route not triggered or triggers too early",
        },
        "acquisition": {
            "route": ACQUISITION_ROUTE,
            "source_file": SOURCE_FILES["acquisition"],
            "center_section": "Stages 24 -> 25 -> 28 -> 29 -> 30",
            "what": "Buyer/acquirer package",
            "why": "Strategic value exists through moat, value capture, and acquirer fit",
            "when": "Moat + value capture + acquirer fit pass",
            "trigger_source": ["thesis", "business model", "acquirer signal families"],
            "required_scores": {
                "moat": {">=": 0.50},
                "value_capture": {">=": 0.55},
                "acquirer_fit": {">=": 0.50},
            },
            "sequence": [24, 25, 28, 29, 30],
            "output": "Acquisition package with buyer rationale, fit, and valuation",
            "failure_state": "Package becomes generic; fallback to portfolio",
        },
        RECURSIVE_MEMORY_ROUTE_ID: {
            "route": RECURSIVE_MEMORY_ROUTE_ID,
            "source_file": SOURCE_FILES["recursive_memory"],
            "center_section": "Post-Stage-30",
            "what": "Future intelligence reinforcement",
            "why": "Approved output strengthens future runs",
            "when": "Output approved + replayable lineage",
            "trigger_source": ["operator approval", "evidence lineage"],
            "required_scores": {
                "output_quality": {">=": 0.60},
                "traceability": {">=": 0.75},
                "replayability": {">=": 0.70},
            },
            "sequence": ["output", "memory", "replay"],
            "output": "Improved future runs through pattern reinforcement",
            "failure_state": "Memory commits unapproved output; blocked",
        },
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "source_contract": "operator_route_files",
        "center_route_contract": build_center_route_contract(),
        "route_count": len(contracts),
        "routes": contracts,
        "causal_intake_status": {
            "status": "deferred_until_route_and_emergence_contracts_are_clean",
            "reason": "Causal bubble files depend on stable route ownership and emergence contracts.",
            "received_causal_contract_files": [
                "C:/Users/craig/OneDrive/Desktop/routes/THE COMPLETE CAUSAL BUBBLE MODEL.txt",
                "C:/Users/craig/OneDrive/Desktop/routes/5 CAUSAL QUESTIONS.txt",
                "C:/Users/craig/OneDrive/Desktop/routes/CAUSAL TIMELINE RECONSTRUCTOR.txt",
                "C:/Users/craig/OneDrive/Desktop/routes/civilization‑scale causal reconstruction engine.txt",
                "C:/Users/craig/OneDrive/Desktop/routes/“global similarity engine.”.txt",
                "C:/Users/craig/OneDrive/Desktop/routes/TimelineEvent.txt",
            ],
        },
    }


def _evaluate_named_gate(outputs: dict[str, Any], route_id: str) -> dict[str, Any]:
    scores = outputs.get("scores") if isinstance(outputs.get("scores"), dict) else {}
    lookup = {
        "trend_strength": _float_or_none(_first_value(outputs, ["trend_discovery.trend_strength", "trend_strength"]) or scores.get("trend_strength")),
        "thesis_quality": _float_or_none(_first_value(outputs, ["thesis_formation.thesis_quality", "thesis_quality"]) or scores.get("thesis_quality")),
        "portfolio_relevance": _float_or_none(_first_value(outputs, ["market_gap.portfolio_relevance.score", "market_gap.portfolio_relevance", "portfolio_relevance"]) or scores.get("portfolio_relevance")),
        "risk_exposure": _float_or_none(_first_value(outputs, ["risk.risk_exposure", "risk_exposure"]) or scores.get("risk_exposure")),
        "gap_validity": _float_or_none(_first_value(outputs, ["market_gap.gap_validity", "gap_validity"]) or scores.get("gap_validity")),
        "gap_severity": _float_or_none(_first_value(outputs, ["market_gap.gap_severity", "gap_severity"]) or scores.get("gap_severity")),
        "breakthrough_threshold": _breakthrough_threshold(outputs, _extract_breakthrough(outputs)),
        "technology_signal": _float_or_none(_first_value(outputs, ["technology_signal", "technology_intelligence.score"]) or scores.get("technology_signal")),
        "buildability_readiness": _float_or_none(_first_value(outputs, ["technical_feasibility.buildability_readiness", "buildability_readiness"]) or scores.get("buildability_readiness")),
        "design_route_readiness": _float_or_none(_first_value(outputs, ["design_portal.design_route_readiness", "design_route_readiness"]) or scores.get("design_route_readiness")),
        "moat": _float_or_none(_first_value(outputs, ["moat.moat_type.moat_score", "moat.score", "moat"]) or scores.get("moat")),
        "value_capture": _float_or_none(_first_value(outputs, ["business_model.value_capture.score", "value_capture"]) or scores.get("value_capture")),
        "acquirer_fit": _float_or_none(_first_value(outputs, ["deal_exit_modeling.acquirer_fit", "acquirer_fit"]) or scores.get("acquirer_fit") or scores.get("acquisition_score")),
        "output_quality": _float_or_none(_first_value(outputs, ["output_quality"]) or scores.get("output_quality")),
        "traceability": _float_or_none(_first_value(outputs, ["traceability"]) or scores.get("traceability")),
        "replayability": _float_or_none(_first_value(outputs, ["replayability"]) or scores.get("replayability")),
    }
    contracts = build_route_contracts()["routes"]
    contract = contracts.get(route_id, contracts["portfolio"])
    checks = []
    for name, rule in contract["required_scores"].items():
        value = lookup.get(name)
        if ">=" in rule:
            threshold = float(rule[">="])
            passed = _pass_min(value, threshold)
            operator = ">="
        else:
            threshold = float(rule["<="])
            passed = _pass_max(value, threshold)
            operator = "<="
        checks.append({"score": name, "value": value, "operator": operator, "threshold": threshold, "passed": passed})
    return {"route_id": route_id, "status": _gate_status(checks), "checks": checks}


def select_route_by_center_contract(outputs: dict[str, Any] | None) -> dict[str, Any]:
    outputs = outputs or {}
    breakthrough = _extract_breakthrough(outputs)
    threshold = _breakthrough_threshold(outputs, breakthrough)
    primary = _breakthrough_primary(outputs, breakthrough)

    if breakthrough is None:
        route_id = "portfolio"
        route = PORTFOLIO_ROUTE
        reason = "breakthrough is None"
        used_center_contract = False
    elif threshold is not None and threshold < 0.55:
        route_id = "portfolio"
        route = PORTFOLIO_ROUTE
        reason = "breakthrough_threshold below 0.55"
        used_center_contract = True
    elif _family_contains(primary, MARKET_FAMILY):
        route_id = "portfolio"
        route = PORTFOLIO_ROUTE
        reason = "breakthrough primary is in MARKET_FAMILY"
        used_center_contract = True
    elif _family_contains(primary, ACQUISITION_FAMILY):
        route_id = "acquisition"
        route = ACQUISITION_ROUTE
        reason = "breakthrough primary is in ACQUISITION_FAMILY"
        used_center_contract = True
    elif _family_contains(primary, TECH_FAMILY):
        route_id = TECH_DESIGN_BUILD_ROUTE_ID
        route = BREAKTHROUGH_DESIGN_ROUTE
        reason = "breakthrough primary is in TECH_FAMILY"
        used_center_contract = True
    elif _family_contains(primary, SYSTEM_REPLACEMENT_FAMILY):
        route_id = "system_replacement"
        route = EXISTING_SYSTEM_REPLACEMENT_ROUTE
        reason = "breakthrough primary is SYSTEM_REPLACEMENT"
        used_center_contract = True
    else:
        route_id = "breakthrough"
        route = BREAKTHROUGH_ESCALATION_ROUTE
        reason = "breakthrough exists and no narrower family matched"
        used_center_contract = True

    gate_id = route_id if route_id in build_route_contracts()["routes"] else "breakthrough"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "selected_route": route,
        "selected_route_id": route_id,
        "used_center_contract": used_center_contract,
        "reason": reason,
        "breakthrough_primary": primary,
        "breakthrough_threshold": threshold,
        "gate": _evaluate_named_gate(outputs, gate_id),
        "authority": {
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
            "dashboard_may_render_only": True,
        },
    }
