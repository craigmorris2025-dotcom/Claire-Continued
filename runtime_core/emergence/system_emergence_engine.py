from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from runtime_core.technology.reemergence_pattern_engine import build_reemergence_pattern_engine


SCHEMA_VERSION = "claire.system_emergence_engine.v1"


@dataclass
class EmergenceCycleRecord:
    cycle_id: str
    timestamp: datetime
    entity_id: str
    predicted_stage: str
    predicted_patterns: list[str]
    readiness_score: float
    route_taken: str
    outcome_label: str | None = None
    notes: str | None = None


class EmergenceMemoryStore:
    def __init__(self) -> None:
        self._records: list[EmergenceCycleRecord] = []

    def append(self, record: EmergenceCycleRecord) -> None:
        self._records.append(record)

    def update_outcome(self, cycle_id: str, outcome_label: str, notes: str | None = None) -> None:
        for index, record in enumerate(self._records):
            if record.cycle_id == cycle_id:
                self._records[index] = EmergenceCycleRecord(
                    **{
                        **asdict(record),
                        "timestamp": record.timestamp,
                        "outcome_label": outcome_label,
                        "notes": notes,
                    }
                )
                return

    def iter_all(self) -> list[EmergenceCycleRecord]:
        return list(self._records)


class EmergencePatternReinforcer:
    def __init__(self, emergence_store: EmergenceMemoryStore):
        self._store = emergence_store

    def compute_pattern_confidence(self) -> dict[str, float]:
        stats: dict[str, dict[str, int]] = {}
        for record in self._store.iter_all():
            for pattern_id in record.predicted_patterns:
                stats.setdefault(pattern_id, {"hit": 0, "miss": 0})
                if record.outcome_label in {"hit", "miss"}:
                    stats[pattern_id][record.outcome_label] += 1
        confidences: dict[str, float] = {}
        for pattern_id, counts in stats.items():
            total = counts["hit"] + counts["miss"]
            confidences[pattern_id] = 0.5 if total == 0 else round(counts["hit"] / total, 3)
        return confidences


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value or 0.0))), 4)


def _records_from_memory(memory_records: Any) -> list[dict[str, Any]]:
    return [item for item in _as_list(memory_records) if isinstance(item, dict)]


def _pattern_memory(memory_records: list[dict[str, Any]]) -> dict[str, Any]:
    pattern_counts: Counter[str] = Counter()
    route_counts: Counter[str] = Counter()
    stage_counts: Counter[str] = Counter()
    for record in memory_records:
        result = _as_dict(record.get("result"))
        route = str(result.get("route_selected") or "unknown")
        route_counts[route] += 1
        emergence = _as_dict(result.get("emergence_engine"))
        for pattern in _as_list(emergence.get("detected_patterns")):
            if isinstance(pattern, dict):
                pattern_id = pattern.get("pattern_id")
            else:
                pattern_id = pattern
            if pattern_id:
                pattern_counts[str(pattern_id)] += 1
        cycle_stage = emergence.get("cycle_stage")
        if cycle_stage:
            stage_counts[str(cycle_stage)] += 1
    return {
        "run_count": len(memory_records),
        "pattern_counts": dict(pattern_counts),
        "route_counts": dict(route_counts),
        "cycle_stage_counts": dict(stage_counts),
        "dominant_pattern": pattern_counts.most_common(1)[0][0] if pattern_counts else None,
        "dominant_route": route_counts.most_common(1)[0][0] if route_counts else None,
    }


def build_system_emergence_engine(
    query: str | None = "",
    *,
    context: dict[str, Any] | None = None,
    memory_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the system-level emergence contract.

    This is the product layer above the ACS2/re-emergence classifier. It answers:
    what pattern is forming, how ready it is, whether Claire can route it, whether
    the current run can learn from it, and what still blocks autonomous promotion.
    """

    context = context or {}
    memory = _records_from_memory(memory_records)
    advancement = _as_dict(context.get("advancement_path_decision"))
    trend_trajectory = _as_dict(context.get("trend_trajectory"))
    source_authority = _as_dict(context.get("source_authority"))
    quality_gate = _as_dict(context.get("quality_gate"))

    reemergence = _as_dict(context.get("reemergence_pattern_engine"))
    if not reemergence:
        reemergence = build_reemergence_pattern_engine(
            query,
            {
                "signals": context.get("signals") or context.get("governed_signals") or context.get("connector_sources"),
                "timeline": trend_trajectory,
                "categories": context.get("domain"),
            },
        )

    signal_families = _as_dict(reemergence.get("signal_families"))
    ready_families = [family_id for family_id, family in signal_families.items() if _as_dict(family).get("ready") is True]
    detected_patterns = _as_list(reemergence.get("detected_patterns"))
    readiness_score = _score(reemergence.get("readiness_score", 0.0))
    route_selected = str(
        advancement.get("route_selected")
        or context.get("route_selected")
        or _as_dict(reemergence.get("route_guidance")).get("recommended_route")
        or "research_monitoring"
    )
    live_evidence_present = bool(
        source_authority.get("live_evidence_present")
        or source_authority.get("source_evidence_present")
        or context.get("signals")
        or context.get("governed_signals")
    )
    memory_signal = _pattern_memory(memory)
    emergence_store = EmergenceMemoryStore()
    for record in memory:
        result = _as_dict(record.get("result"))
        emergence_result = _as_dict(result.get("emergence_engine"))
        patterns = [
            str(item.get("pattern_id"))
            for item in _as_list(emergence_result.get("detected_patterns"))
            if isinstance(item, dict) and item.get("pattern_id")
        ]
        if patterns:
            emergence_store.append(
                EmergenceCycleRecord(
                    cycle_id=str(record.get("run_id") or result.get("run_id") or "memory_record"),
                    timestamp=datetime.now(timezone.utc),
                    entity_id=str(result.get("domain") or context.get("domain") or "unknown"),
                    predicted_stage=str(emergence_result.get("cycle_stage") or "unknown"),
                    predicted_patterns=patterns,
                    readiness_score=float(emergence_result.get("readiness_score") or 0.0),
                    route_taken=str(result.get("route_selected") or "unknown"),
                    outcome_label=result.get("outcome_label"),
                )
            )
    pattern_confidence = EmergencePatternReinforcer(emergence_store).compute_pattern_confidence()
    memory_depth_score = _score(min(1.0, len(memory) / 50.0))
    runtime_route_score = _score(
        1.0
        if route_selected in {"portfolio_creation_optimization", "breakthrough_design", "existing_system_replacement"}
        else 0.55
        if route_selected != "research_monitoring"
        else 0.25
    )
    evidence_score = _score(1.0 if live_evidence_present else 0.55)
    pattern_score = _score(min(1.0, len(detected_patterns) / 3.0))
    signal_score = _score(len(ready_families) / 7.0)
    trajectory_score = _score(
        trend_trajectory.get("confidence")
        or _as_dict(trend_trajectory.get("market_momentum")).get("score")
        or readiness_score
    )
    learning_score = _score(1.0 if quality_gate.get("recursive_learning_complete") else 0.72 if memory else 0.35)

    area_scores = {
        "acs2_pattern_mass": _score(1.0 if detected_patterns else 0.45),
        "signal_family_readiness": signal_score,
        "reemergence_classification": _score(readiness_score),
        "trend_trajectory_binding": trajectory_score,
        "runtime_route_binding": runtime_route_score,
        "live_evidence_governance": evidence_score,
        "recursive_learning_depth": learning_score,
        "longitudinal_memory_depth": memory_depth_score,
    }
    product_completion_percent = round(sum(area_scores.values()) / len(area_scores) * 100, 1)

    blockers: list[str] = []
    if not detected_patterns:
        blockers.append("no_reemergence_pattern_detected")
    if len(ready_families) < 3:
        blockers.append("insufficient_signal_family_readiness")
    if not live_evidence_present:
        blockers.append("live_or_governed_evidence_missing")
    if len(memory) < 50:
        blockers.append("needs_50_to_200_lived_cycles_for_mature_learning")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "emergence_engine_operational" if product_completion_percent >= 70 else "emergence_engine_foundation_ready",
        "query": str(query or ""),
        "product_completion_percent": product_completion_percent,
        "maturity": (
            "mature_foundation_not_autonomous_promotion"
            if product_completion_percent >= 85
            else "active_foundation_needs_more_lived_cycles"
        ),
        "cycle_stage": reemergence.get("cycle_stage"),
        "route_selected": route_selected,
        "route_guidance": reemergence.get("route_guidance", {}),
        "readiness_score": readiness_score,
        "area_scores": area_scores,
        "detected_patterns": [
            {
                "pattern_id": item.get("pattern_id"),
                "name": item.get("name"),
                "score": item.get("score"),
                "primary_signal_families": item.get("primary_signal_families", []),
            }
            for item in detected_patterns[:8]
            if isinstance(item, dict)
        ],
        "ready_signal_families": ready_families,
        "signals_to_watch": reemergence.get("signals_to_watch", []),
        "longitudinal_learning": memory_signal,
        "pattern_reinforcement": {
            "status": "active" if pattern_confidence else "waiting_for_labeled_outcomes",
            "pattern_confidence": pattern_confidence,
            "recordable_cycle_contract": "cycle_id, entity_id, predicted_stage, predicted_patterns, readiness_score, route_taken, outcome_label",
        },
        "pipeline_bindings": {
            **_as_dict(reemergence.get("pipeline_bindings")),
            "whole_system": "signal intake -> ACS2 analogy -> re-emergence scoring -> route selection -> invention/design/portfolio -> acquisition/package -> recursive learning",
        },
        "remaining_blockers_to_maturity": blockers,
        "authority": {
            "network_request_performed": False,
            "runtime_truth_mutation": False,
            "autonomous_promotion_allowed": False,
            "operator_review_required": True,
            "documents_used_as_runtime_programming": False,
        },
    }


__all__ = [
    "EmergenceCycleRecord",
    "EmergenceMemoryStore",
    "EmergencePatternReinforcer",
    "SCHEMA_VERSION",
    "build_system_emergence_engine",
]
