from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, replace
from typing import Any

from runtime_core.signals.signal_timeseries_store import SignalSeries, SignalTimeSeriesStore, default_signal_timeseries_store


SCHEMA_VERSION = "claire.acs2_reemergence_pattern_engine.v2"


@dataclass(frozen=True)
class RequiredSignalChange:
    signal_id: str
    direction: str
    threshold_type: str
    heuristic_threshold: float | None = None
    learned_threshold: float | None = None
    window_years: int | None = None


@dataclass(frozen=True)
class ReemergencePattern:
    pattern_id: str
    name: str
    description: str
    primary_signal_families: list[str]
    required_changes: list[RequiredSignalChange]
    historical_examples: list[str]
    typical_lag_years: list[int]
    keywords: list[str]


SIGNAL_FAMILIES: dict[str, dict[str, Any]] = {
    "technology": {
        "description": "Enabling capability movement from not-ready to ready.",
        "signals": [
            "compute_per_dollar",
            "storage_per_dollar",
            "bandwidth_latency",
            "battery_density",
            "sensor_cost_accuracy",
            "model_capability",
            "automation_potential",
        ],
        "keywords": [
            "compute",
            "storage",
            "bandwidth",
            "latency",
            "battery",
            "sensor",
            "model",
            "ai",
            "lithium",
            "touch",
            "processor",
            "miniaturization",
            "automation",
            "agent",
            "copilot",
            "llm",
        ],
    },
    "cost": {
        "description": "Unit economics, margins, scale, and payback crossing viability thresholds.",
        "signals": ["unit_cost", "gross_margin", "capex_opex_intensity", "payback_period", "scale_economies"],
        "keywords": ["cost", "margin", "capex", "opex", "payback", "scale", "economies", "cheap", "affordable"],
    },
    "distribution": {
        "description": "Access paths that let demand reach the market.",
        "signals": [
            "internet_penetration",
            "smartphone_penetration",
            "logistics_coverage",
            "platform_access",
            "enterprise_it_readiness",
            "attention_shift",
            "device_shift",
        ],
        "keywords": ["distribution", "internet", "smartphone", "logistics", "app", "platform", "cloud", "enterprise", "attention", "device", "channel"],
    },
    "regulation": {
        "description": "Legality, compliance cost, licensing, privacy, subsidy, and incentive readiness.",
        "signals": ["legality", "compliance_cost", "licensing_requirements", "privacy_constraints", "subsidies"],
        "keywords": ["regulation", "policy", "legal", "compliance", "license", "privacy", "subsidy", "incentive"],
    },
    "behavior": {
        "description": "Culture, trust, data sharing, work style, and adoption preference shifts.",
        "signals": ["remote_preference", "digital_trust", "data_sharing_willingness", "time_spent", "macro_shock", "workflow_complexity"],
        "keywords": ["behavior", "culture", "remote", "trust", "consumer", "subscription", "fatigue", "habit", "workflow", "vertical"],
    },
    "infrastructure": {
        "description": "Physical and digital substrate availability.",
        "signals": ["charging_networks", "cloud_infra", "data_centers", "5g_fiber_coverage", "logistics_hubs"],
        "keywords": ["infrastructure", "charging", "network", "fiber", "5g", "datacenter", "data center", "hub", "grid"],
    },
    "ecosystem": {
        "description": "Platform dominance, complements, competition, fragmentation, and consolidation.",
        "signals": ["platform_dominance", "player_count", "fragmentation", "consolidation", "complements", "industry_fragmentation"],
        "keywords": ["ecosystem", "competition", "fragmentation", "consolidation", "complement", "bundle", "suite", "lock in"],
    },
}


PATTERN_DEFINITIONS: list[dict[str, Any]] = [
    {
        "pattern_id": "technology_catch_up",
        "name": "Technology Catch-Up Re-Emergence",
        "description": "Market returns when enabling technology crosses viability thresholds.",
        "primary_signal_families": ["technology", "cost"],
        "required_signal_changes": [
            {"signal": "battery_energy_density", "direction": "up", "threshold_type": "absolute_or_relative"},
            {"signal": "compute_per_dollar", "direction": "up", "threshold_type": "relative"},
            {"signal": "unit_cost", "direction": "down", "threshold_type": "relative"},
        ],
        "historical_examples": ["EVs", "VR", "tablets"],
        "typical_lag_years": [10, 30],
        "keywords": ["tablet", "vr", "ar", "electric", "ev", "battery", "compute", "sensor", "lithium", "smart"],
    },
    {
        "pattern_id": "distribution_inversion",
        "name": "Distribution Inversion Re-Emergence",
        "description": "A failed product returns when the access channel changes.",
        "primary_signal_families": ["distribution", "behavior", "regulation"],
        "required_signal_changes": [
            {"signal": "distribution_access", "direction": "up", "threshold_type": "coverage"},
            {"signal": "behavioral_acceptance", "direction": "up", "threshold_type": "adoption"},
        ],
        "historical_examples": ["telehealth", "online groceries", "remote work"],
        "typical_lag_years": [5, 25],
        "keywords": ["telehealth", "remote", "online", "delivery", "logistics", "broadband", "app", "mobile"],
    },
    {
        "pattern_id": "cost_collapse",
        "name": "Cost Collapse Re-Emergence",
        "description": "Market becomes viable after cost curves drop below adoption thresholds.",
        "primary_signal_families": ["cost", "technology", "infrastructure"],
        "required_signal_changes": [
            {"signal": "unit_cost", "direction": "down", "threshold_type": "relative"},
            {"signal": "scale_economies", "direction": "up", "threshold_type": "curve"},
        ],
        "historical_examples": ["solar", "DNA sequencing", "3D printing", "cloud computing"],
        "typical_lag_years": [5, 20],
        "keywords": ["solar", "sequencing", "3d printing", "cloud", "cost", "cheap", "scale"],
    },
    {
        "pattern_id": "platformization",
        "name": "Platformization Re-Emergence",
        "description": "A niche product returns as a feature or app inside a broader platform.",
        "primary_signal_families": ["technology", "distribution", "ecosystem"],
        "required_signal_changes": [
            {"signal": "capability_stacking", "direction": "up", "threshold_type": "convergence"},
            {"signal": "platform_access", "direction": "up", "threshold_type": "ecosystem"},
        ],
        "historical_examples": ["GPS to smartphone GPS", "MP3 players to smartphone music", "PDAs to smartphones"],
        "typical_lag_years": [5, 15],
        "keywords": ["platform", "smartphone", "app", "gps", "mp3", "pda", "tablet", "mobile", "convergence"],
    },
    {
        "pattern_id": "unbundle_rebundle",
        "name": "Unbundling Rebundling Re-Emergence",
        "description": "A product breaks apart, then returns as an integrated bundle after user fatigue or integration demand.",
        "primary_signal_families": ["ecosystem", "behavior", "cost"],
        "required_signal_changes": [
            {"signal": "fragmentation_index", "direction": "up_then_down", "threshold_type": "cycle"},
            {"signal": "integration_demand", "direction": "up", "threshold_type": "behavior"},
        ],
        "historical_examples": ["cable to streaming bundles", "SaaS suites", "embedded finance"],
        "typical_lag_years": [3, 15],
        "keywords": ["bundle", "rebundle", "unbundle", "suite", "streaming", "embedded", "fatigue"],
    },
    {
        "pattern_id": "regulation_driven",
        "name": "Regulation-Driven Re-Emergence",
        "description": "A market returns because legality or compliance conditions shift.",
        "primary_signal_families": ["regulation", "cost", "distribution"],
        "required_signal_changes": [
            {"signal": "legality", "direction": "up", "threshold_type": "policy"},
            {"signal": "compliance_cost", "direction": "down", "threshold_type": "relative"},
        ],
        "historical_examples": ["cannabis", "crypto custody", "telehealth", "autonomous vehicles"],
        "typical_lag_years": [3, 25],
        "keywords": ["regulation", "policy", "compliance", "custody", "cannabis", "telehealth", "autonomous vehicle"],
    },
    {
        "pattern_id": "behavior_shift",
        "name": "Behavior Shift Re-Emergence",
        "description": "A market returns because customer habits, trust, demographics, or shocks change.",
        "primary_signal_families": ["behavior", "distribution", "ecosystem"],
        "required_signal_changes": [
            {"signal": "behavioral_acceptance", "direction": "up", "threshold_type": "adoption"},
            {"signal": "trust_in_digital", "direction": "up", "threshold_type": "culture"},
        ],
        "historical_examples": ["home fitness", "meal kits", "neobanks", "personal finance tools"],
        "typical_lag_years": [3, 20],
        "keywords": ["fitness", "meal", "neobank", "personal finance", "subscription", "remote", "trust"],
    },
    {
        "pattern_id": "infrastructure_catch_up",
        "name": "Infrastructure Catch-Up Re-Emergence",
        "description": "A market returns when the surrounding physical or digital infrastructure becomes dense enough.",
        "primary_signal_families": ["infrastructure", "technology", "distribution"],
        "required_signal_changes": [
            {"signal": "deployment_density", "direction": "up", "threshold_type": "coverage"},
            {"signal": "reliability", "direction": "up", "threshold_type": "operational"},
        ],
        "historical_examples": ["EV charging networks", "drone delivery", "smart homes", "IoT"],
        "typical_lag_years": [5, 30],
        "keywords": ["charging", "drone", "smart home", "iot", "5g", "fiber", "cloud", "grid", "network"],
    },
    {
        "pattern_id": "ecosystem_lock_in",
        "name": "Ecosystem Lock-In Re-Emergence",
        "description": "A product returns because it becomes part of a larger platform ecosystem.",
        "primary_signal_families": ["ecosystem", "distribution", "behavior"],
        "required_signal_changes": [
            {"signal": "platform_dominance", "direction": "up", "threshold_type": "ecosystem"},
            {"signal": "complements", "direction": "up", "threshold_type": "ecosystem"},
        ],
        "historical_examples": ["smartwatches to Apple Watch", "home assistants to Alexa and Google ecosystems"],
        "typical_lag_years": [3, 15],
        "keywords": ["ecosystem", "apple watch", "smartwatch", "assistant", "alexa", "google", "platform dominance", "complement"],
    },
    {
        "pattern_id": "ai_native",
        "name": "AI-Native Re-Emergence",
        "description": "A product returns because AI capability makes the old use case viable.",
        "primary_signal_families": ["technology", "cost", "ecosystem"],
        "required_signal_changes": [
            {"signal": "model_capability", "direction": "up", "threshold_type": "capability_curve"},
            {"signal": "automation_potential", "direction": "up", "threshold_type": "workflow"},
        ],
        "historical_examples": ["personal assistants to AI copilots", "chatbots to LLM agents", "robotics to AI-driven robotics"],
        "typical_lag_years": [2, 20],
        "keywords": ["ai", "agent", "agents", "copilot", "chatbot", "llm", "robotics", "automation", "model capability"],
    },
    {
        "pattern_id": "verticalization",
        "name": "Verticalization Re-Emergence",
        "description": "A horizontal product returns as a vertical stack for a specific industry workflow.",
        "primary_signal_families": ["ecosystem", "distribution", "behavior"],
        "required_signal_changes": [
            {"signal": "industry_fragmentation", "direction": "up", "threshold_type": "market_structure"},
            {"signal": "workflow_complexity", "direction": "up", "threshold_type": "workflow"},
        ],
        "historical_examples": ["CRM to vertical CRM", "ERP to vertical ERP", "payments to vertical payments"],
        "typical_lag_years": [3, 15],
        "keywords": ["vertical", "verticalized", "crm", "erp", "payments", "workflow", "industry fragmentation", "specialized"],
    },
    {
        "pattern_id": "modality_shift",
        "name": "Modality Shift Re-Emergence",
        "description": "A product returns in a new medium, device mode, or attention channel.",
        "primary_signal_families": ["distribution", "behavior", "technology"],
        "required_signal_changes": [
            {"signal": "attention_shift", "direction": "up", "threshold_type": "channel"},
            {"signal": "device_shift", "direction": "up", "threshold_type": "modality"},
        ],
        "historical_examples": ["radio to podcasts", "newspapers to newsletters", "TV to streaming", "retail to social commerce"],
        "typical_lag_years": [3, 25],
        "keywords": ["modality", "podcast", "newsletter", "streaming", "social commerce", "attention", "device", "content"],
    },
]


def pattern_objects() -> list[ReemergencePattern]:
    patterns: list[ReemergencePattern] = []
    signal_aliases = {
        "battery_energy_density": "battery_energy_density",
        "compute_per_dollar": "compute_per_dollar",
        "unit_cost": "unit_cost",
        "distribution_access": "broadband_penetration",
        "behavioral_acceptance": "regulatory_acceptance",
        "scale_economies": "unit_cost",
        "capability_stacking": "compute_per_dollar",
        "platform_access": "touch_interface_readiness",
        "fragmentation_index": "platform_access",
        "integration_demand": "platform_access",
        "legality": "regulatory_acceptance",
        "compliance_cost": "unit_cost",
        "trust_in_digital": "broadband_penetration",
        "deployment_density": "charging_network_density",
        "reliability": "sensor_cost_accuracy",
        "platform_dominance": "platform_access",
        "complements": "platform_access",
        "model_capability": "model_capability",
        "automation_potential": "model_capability",
        "industry_fragmentation": "fragmentation",
        "workflow_complexity": "platform_access",
        "attention_shift": "broadband_penetration",
        "device_shift": "touch_interface_readiness",
    }
    for definition in PATTERN_DEFINITIONS:
        required = []
        for item in definition.get("required_signal_changes", []):
            signal = str(item.get("signal") or "")
            direction = str(item.get("direction") or "up")
            required.append(
                RequiredSignalChange(
                    signal_id=signal_aliases.get(signal, signal),
                    direction="down" if direction == "down" else "up",
                    threshold_type=str(item.get("threshold_type") or "relative"),
                    heuristic_threshold=0.10 if direction != "down" else -0.10,
                    window_years=5,
                )
            )
        patterns.append(
            ReemergencePattern(
                pattern_id=definition["pattern_id"],
                name=definition["name"],
                description=definition["description"],
                primary_signal_families=list(definition["primary_signal_families"]),
                required_changes=required,
                historical_examples=list(definition["historical_examples"]),
                typical_lag_years=list(definition["typical_lag_years"]),
                keywords=list(definition["keywords"]),
            )
        )
    return patterns


CATEGORY_MAP: dict[str, dict[str, Any]] = {
    "technology": {
        "name": "Technology",
        "subcategories": [
            "computing",
            "mobile",
            "wearables",
            "smart_home",
            "robotics",
            "ai_agents",
            "cloud_saas",
            "networking",
            "sensors_iot",
            "gaming_hardware",
            "ar_vr_xr",
            "consumer_electronics",
        ],
        "route_bias": ["technology_catch_up", "platformization", "cost_collapse"],
        "transformation_focus": "ACS2 object families, enabling technology, platformization, and AI-native capability curves.",
    },
    "automotive_transportation": {
        "name": "Automotive & Transportation",
        "subcategories": ["cars", "evs", "autonomous_vehicles", "motorcycles", "bicycles_ebikes", "public_transit", "aviation", "drones", "logistics_delivery", "marine"],
        "route_bias": ["technology_catch_up", "infrastructure_catch_up", "regulation_driven"],
        "transformation_focus": "Mobility transformation, infrastructure catch-up, autonomy, energy convergence, and regulation.",
    },
    "clothing_apparel": {
        "name": "Clothing & Apparel",
        "subcategories": ["everyday_wear", "sportswear", "luxury", "workwear", "footwear", "accessories", "smart_clothing", "outdoor_gear"],
        "route_bias": ["behavior_shift", "technology_catch_up", "platformization"],
        "transformation_focus": "Material innovation, sensorization, fashion cycles, and wearable convergence.",
    },
    "home_living": {
        "name": "Home & Living",
        "subcategories": ["furniture", "appliances", "smart_home_devices", "kitchenware", "cleaning_tools", "home_energy", "security", "home_fitness"],
        "route_bias": ["infrastructure_catch_up", "behavior_shift", "technology_catch_up"],
        "transformation_focus": "Automation, energy, smart-home convergence, behavior shifts, and infrastructure readiness.",
    },
    "health_wellness": {
        "name": "Health & Wellness",
        "subcategories": ["medical_devices", "supplements", "fitness_equipment", "telehealth", "wearable_health", "diagnostics", "mental_health", "personal_care"],
        "route_bias": ["distribution_inversion", "regulation_driven", "technology_catch_up"],
        "transformation_focus": "Biotech, sensorization, telehealth distribution, regulation, and AI-health convergence.",
    },
    "finance_commerce": {
        "name": "Finance & Commerce",
        "subcategories": ["banking", "payments", "insurance", "investing", "fintech", "e_commerce", "point_of_sale", "subscriptions", "loyalty_rewards"],
        "route_bias": ["platformization", "unbundle_rebundle", "regulation_driven"],
        "transformation_focus": "Platformization, embedded finance, rebundling, identity, payments, and compliance shifts.",
    },
    "entertainment_media": {
        "name": "Entertainment & Media",
        "subcategories": ["movies_tv", "streaming", "music", "gaming", "books", "social_media", "podcasts", "creator_tools"],
        "route_bias": ["distribution_inversion", "unbundle_rebundle", "platformization", "modality_shift"],
        "transformation_focus": "Modality shifts, attention cycles, distribution inversion, creator tooling, and bundling cycles.",
    },
    "industrial_infrastructure": {
        "name": "Industrial & Infrastructure",
        "subcategories": ["energy", "manufacturing", "construction", "agriculture", "logistics", "defense", "utilities", "materials"],
        "route_bias": ["cost_collapse", "infrastructure_catch_up", "technology_catch_up", "ai_native"],
        "transformation_focus": "Cost collapse, automation, materials, infrastructure deployment, and AI-driven transformation.",
    },
}


def _terms(text: str | None) -> list[str]:
    stop = {"and", "the", "for", "with", "from", "this", "that", "into", "will", "should", "market"}
    tokens: list[str] = []
    for raw in re.split(r"[^a-z0-9]+", str(text or "").lower()):
        if len(raw) < 3 or raw in stop:
            continue
        tokens.append(raw)
    return tokens


def _phrase_hits(text: str, values: list[str]) -> list[str]:
    hits: list[str] = []
    for value in values:
        needle = value.lower()
        if " " in needle:
            if needle in text:
                hits.append(value)
        elif needle in text:
            hits.append(value)
    return hits


def _score_signal_families(text: str) -> dict[str, Any]:
    families: dict[str, Any] = {}
    for family_id, family in SIGNAL_FAMILIES.items():
        keyword_hits = _phrase_hits(text, family["keywords"])
        signal_hits = _phrase_hits(text.replace("_", " "), [item.replace("_", " ") for item in family["signals"]])
        score = min(1.0, (len(keyword_hits) * 0.18) + (len(signal_hits) * 0.22))
        families[family_id] = {
            "score": round(score, 3),
            "ready": score >= 0.34,
            "keyword_hits": keyword_hits[:8],
            "signal_hits": signal_hits[:8],
            "signals": family["signals"],
        }
    return families


def _score_categories(text: str) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for category_id, category in CATEGORY_MAP.items():
        terms = [category_id.replace("_", " "), *[item.replace("_", " ") for item in category["subcategories"]]]
        hits = _phrase_hits(text, terms)
        score = min(1.0, len(hits) * 0.24)
        if score:
            scored.append(
                {
                    "category_id": category_id,
                    "score": round(score, 3),
                    "hits": hits[:8],
                    "route_bias": category["route_bias"],
                }
            )
    return sorted(scored, key=lambda item: item["score"], reverse=True)


def _pattern_scores(text: str, family_scores: dict[str, Any], categories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    category_biases = Counter(pattern for category in categories for pattern in category.get("route_bias", []))
    scored: list[dict[str, Any]] = []
    for pattern in PATTERN_DEFINITIONS:
        family_score = sum(float(family_scores.get(fid, {}).get("score", 0.0)) for fid in pattern["primary_signal_families"]) / max(
            1, len(pattern["primary_signal_families"])
        )
        keyword_hits = _phrase_hits(text, pattern["keywords"])
        keyword_score = min(1.0, len(keyword_hits) * 0.18)
        bias_score = min(0.18, category_biases.get(pattern["pattern_id"], 0) * 0.06)
        score = min(1.0, family_score * 0.58 + keyword_score * 0.32 + bias_score)
        scored.append(
            {
                "pattern_id": pattern["pattern_id"],
                "name": pattern["name"],
                "score": round(score, 3),
                "detected": score >= 0.28,
                "primary_signal_families": pattern["primary_signal_families"],
                "required_signal_changes": pattern["required_signal_changes"],
                "historical_examples": pattern["historical_examples"],
                "typical_lag_years": pattern["typical_lag_years"],
                "keyword_hits": keyword_hits[:8],
            }
        )
    return sorted(scored, key=lambda item: item["score"], reverse=True)


def _cycle_stage(top_score: float, ready_family_count: int, pattern_count: int) -> str:
    if top_score >= 0.72 and ready_family_count >= 4:
        return "post_reemergence_or_active_adoption"
    if top_score >= 0.48 and ready_family_count >= 3:
        return "re_emerging"
    if top_score >= 0.28 and ready_family_count >= 2:
        return "pre_reemergence_watch"
    if pattern_count:
        return "weak_analog_watch"
    return "insufficient_signal"


def _compute_delta(series: SignalSeries, window_years: int) -> float | None:
    points = sorted(series.points, key=lambda point: point.date)
    if len(points) < 2:
        return None
    latest = points[-1]
    cutoff_year = latest.date.year - window_years
    candidates = [point for point in points if point.date.year >= cutoff_year]
    if len(candidates) >= 2:
        earliest = candidates[0]
    else:
        earliest = points[-2]
    return latest.value - earliest.value


class ReemergencePatternEngine:
    def __init__(self, timeseries_store: SignalTimeSeriesStore | None = None, patterns: list[ReemergencePattern] | None = None):
        self._store = timeseries_store or default_signal_timeseries_store()
        self._patterns = {pattern.pattern_id: pattern for pattern in (patterns or pattern_objects())}

    def compute_readiness(self, entity_id: str) -> dict[str, Any]:
        scores = [self._score_pattern_for_entity(pattern, entity_id) for pattern in self._patterns.values()]
        scores.sort(key=lambda item: item["score"], reverse=True)
        detected = [item for item in scores if item["score"] >= 0.30]
        readiness = round(min(1.0, (scores[0]["score"] if scores else 0.0) * 0.72 + len(detected) / max(1, len(scores)) * 0.28), 3)
        return {
            "status": "ready",
            "entity_id": entity_id,
            "readiness_score": readiness,
            "cycle_stage": _cycle_stage(readiness, min(7, len(detected) + 1), len(detected)),
            "pattern_scores": scores,
            "detected_patterns": detected,
            "series_count": len(self._store.list_series_for_entity(entity_id)),
        }

    def _score_pattern_for_entity(self, pattern: ReemergencePattern, entity_id: str) -> dict[str, Any]:
        required_scores = []
        evidence = []
        for req in pattern.required_changes:
            series = self._store.get_series(req.signal_id, entity_id)
            if not series:
                evidence.append({"signal_id": req.signal_id, "status": "missing"})
                continue
            delta = _compute_delta(series, req.window_years or 5)
            threshold = req.learned_threshold if req.learned_threshold is not None else req.heuristic_threshold
            if delta is None or threshold is None:
                signal_score = 0.0
            elif req.direction == "down":
                signal_score = 1.0 if delta <= threshold else max(0.0, min(1.0, abs(threshold) / max(abs(delta), 0.001)))
            else:
                signal_score = 1.0 if delta >= threshold else max(0.0, min(1.0, delta / max(threshold, 0.001)))
            required_scores.append(signal_score)
            evidence.append(
                {
                    "signal_id": req.signal_id,
                    "direction": req.direction,
                    "delta": round(delta, 4) if delta is not None else None,
                    "threshold": threshold,
                    "score": round(signal_score, 3),
                }
            )
        score = sum(required_scores) / max(1, len(pattern.required_changes))
        return {
            "pattern_id": pattern.pattern_id,
            "name": pattern.name,
            "score": round(score, 3),
            "primary_signal_families": pattern.primary_signal_families,
            "historical_examples": pattern.historical_examples,
            "signal_evidence": evidence,
        }


def build_reemergence_pattern_engine(
    query: str | None = "",
    context: dict[str, Any] | None = None,
    timeseries_store: SignalTimeSeriesStore | None = None,
    entity_id: str | None = None,
) -> dict[str, Any]:
    context = context or {}
    context_text = " ".join(
        [
            str(query or ""),
            str(context.get("timeline") or ""),
            str(context.get("signals") or ""),
            str(context.get("categories") or ""),
        ]
    ).lower()
    term_counts = Counter(_terms(context_text))
    signal_families = _score_signal_families(context_text)
    categories = _score_categories(context_text)
    patterns = _pattern_scores(context_text, signal_families, categories)
    series_readiness = {}
    entity = entity_id or context.get("entity_id") or None
    if entity:
        series_readiness = ReemergencePatternEngine(timeseries_store=timeseries_store).compute_readiness(str(entity))
        series_patterns = series_readiness.get("pattern_scores", [])
        series_by_id = {item.get("pattern_id"): item for item in series_patterns if isinstance(item, dict)}
        for pattern in patterns:
            series = series_by_id.get(pattern.get("pattern_id"))
            if not series:
                continue
            pattern["time_series_score"] = series.get("score")
            pattern["score"] = round(min(1.0, float(pattern.get("score", 0.0)) * 0.55 + float(series.get("score", 0.0)) * 0.45), 3)
            pattern["detected"] = pattern["score"] >= 0.28
            pattern["time_series_evidence"] = series.get("signal_evidence", [])
        patterns = sorted(patterns, key=lambda item: item["score"], reverse=True)
    detected = [item for item in patterns if item["detected"]]
    ready_family_count = sum(1 for item in signal_families.values() if item["ready"])
    top_score = float(patterns[0]["score"] if patterns else 0.0)
    pattern_readiness_denominator = min(8, max(1, len(PATTERN_DEFINITIONS)))
    readiness_score = round(
        min(
            1.0,
            (top_score * 0.48)
            + (ready_family_count / max(1, len(SIGNAL_FAMILIES)) * 0.34)
            + (len(detected) / pattern_readiness_denominator * 0.18),
        ),
        3,
    )
    stage = _cycle_stage(top_score, ready_family_count, len(detected))
    route = (
        "breakthrough_design"
        if readiness_score >= 0.64 and stage in {"re_emerging", "post_reemergence_or_active_adoption"}
        else "portfolio_creation_optimization"
        if readiness_score >= 0.36
        else "research_monitoring"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "query": str(query or ""),
        "basis": "Operator ACS2 timeline notes encoded as signal-family and re-emergence pattern contracts.",
        "signal_family_count": len(SIGNAL_FAMILIES),
        "pattern_count": len(PATTERN_DEFINITIONS),
        "category_count": len(CATEGORY_MAP),
        "signal_families": signal_families,
        "category_matches": categories,
        "classified_patterns": patterns,
        "time_series_readiness": series_readiness,
        "detected_patterns": detected,
        "readiness_score": readiness_score,
        "cycle_stage": stage,
        "route_guidance": {
            "recommended_route": route,
            "why": (
                "Pattern and signal readiness are strong enough to generate or validate a breakthrough candidate."
                if route == "breakthrough_design"
                else "Pattern is useful for portfolio/discovery scoring, but needs more live evidence before design promotion."
                if route == "portfolio_creation_optimization"
                else "Signals are too thin for invention routing; keep monitoring."
            ),
        },
        "pipeline_bindings": {
            "stage_1_4": "signal intake, source governance, and family readiness scoring",
            "stage_5_10": "timeline/ACS2 analogy matching and trend thesis formation",
            "stage_11_15": "gap classification, re-emergence pattern scoring, route selection",
            "stage_16_22": "auto invention/design only when pattern readiness and buildability are high",
            "stage_23_30": "portfolio, acquisition, package, evidence review, and recursive learning",
        },
        "signals_to_watch": sorted({signal for pattern in detected[:4] for item in pattern["required_signal_changes"] for signal in [item["signal"]]}),
        "top_terms": [{"term": term, "count": count} for term, count in term_counts.most_common(12)],
        "authority": {
            "network_request_performed": False,
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
            "documents_used_as_runtime_programming": False,
        },
    }


def build_reemergence_taxonomy() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "source_contract": "operator_category_timeline_pattern_notes",
        "source_files": [
            "C:/Users/craig/OneDrive/Desktop/Categories/Primary Main ctaegories.txt",
            "C:/Users/craig/OneDrive/Desktop/Categories/General.txt",
            "C:/Users/craig/OneDrive/Desktop/Categories/PATTERN STRUCTURE.txt",
            "C:/Users/craig/OneDrive/Desktop/Categories/TIMELINE ENGINE.txt",
            "C:/Users/craig/OneDrive/Desktop/Categories/Tracking.txt",
        ],
        "category_count": len(CATEGORY_MAP),
        "signal_family_count": len(SIGNAL_FAMILIES),
        "pattern_count": len(PATTERN_DEFINITIONS),
        "categories": CATEGORY_MAP,
        "signal_families": SIGNAL_FAMILIES,
        "patterns": PATTERN_DEFINITIONS,
        "timeline_engine_contract": {
            "classification_flow": [
                "look at signals over time",
                "match required signal changes",
                "classify re-emergence pattern",
                "estimate cycle stage",
                "score pattern readiness and historical analog similarity",
                "bind to portfolio, breakthrough/design, acquisition, and recursive learning routes",
            ],
            "cycle_stages": [
                "insufficient_signal",
                "weak_analog_watch",
                "pre_reemergence_watch",
                "re_emerging",
                "post_reemergence_or_active_adoption",
            ],
            "minimum_v1_data_contract": {
                "signals": "10-20 concrete signals across the 7 families",
                "pattern_requirements": "3-5 key signal changes per pattern",
                "historical_cases": ["EVs", "VR", "tablets", "telehealth", "streaming"],
                "rendered_outputs": ["market metric", "key signals over time", "pattern label", "re-emergence readiness score"],
            },
        },
        "route_readiness": {
            "routes_may_attach_now": True,
            "emergence_files_may_attach_after_routes": True,
            "causal_files_may_attach_after_emergence_contracts": True,
            "runtime_truth_mutation": False,
            "manual_promotion_required": True,
        },
    }


__all__ = [
    "CATEGORY_MAP",
    "PATTERN_DEFINITIONS",
    "SCHEMA_VERSION",
    "SIGNAL_FAMILIES",
    "RequiredSignalChange",
    "ReemergencePattern",
    "ReemergencePatternEngine",
    "build_reemergence_pattern_engine",
    "build_reemergence_taxonomy",
    "pattern_objects",
]
