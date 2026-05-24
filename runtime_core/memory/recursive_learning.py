from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List


def _keywords(record: Dict[str, Any]) -> List[str]:
    result = record.get("result", {}) if isinstance(record.get("result"), dict) else {}
    values = result.get("keywords", [])
    if not isinstance(values, list):
        return []
    return [str(item).lower() for item in values if str(item).strip()]


def _route(record: Dict[str, Any]) -> str:
    result = record.get("result", {}) if isinstance(record.get("result"), dict) else {}
    return str(result.get("route_selected") or "unknown")


def build_recursive_learning_snapshot(run_spine: Dict[str, Any], memory_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a longitudinal learning snapshot from governed lifecycle memory.

    This implements the intent of the recovered recursive/longitudinal specs:
    signal extraction, recurring gap detection, run-pattern mining, thesis
    evolution, quality scoring, and strategy memory synthesis.
    """

    records = [item for item in memory_records if isinstance(item, dict)]
    route_counts = Counter(_route(item) for item in records)
    keyword_counts: Counter[str] = Counter()
    for item in records:
        keyword_counts.update(_keywords(item))

    current_keywords = [str(item).lower() for item in run_spine.get("trend", {}).get("keywords", []) if str(item).strip()]
    current_route = str(run_spine.get("route_selected") or "unknown")
    emergence = run_spine.get("emergence_engine", {}) if isinstance(run_spine.get("emergence_engine"), dict) else {}
    signal_count = len(run_spine.get("signals", [])) if isinstance(run_spine.get("signals"), list) else 0
    design_proof_ready = (
        run_spine.get("design_candidate", {})
        .get("design_proof", {})
        .get("status")
        == "design_proof_ready"
    )
    recurring_keywords = [
        {"keyword": keyword, "count": count}
        for keyword, count in keyword_counts.most_common(8)
        if count >= 2
    ]
    recurrent_gap_types = []
    quality_gate = run_spine.get("quality_gate", {}) if isinstance(run_spine.get("quality_gate"), dict) else {}
    if not quality_gate.get("acquisition_rationale_present"):
        recurrent_gap_types.append("acquirer_fit_missing")
    if not quality_gate.get("design_proof_complete") and run_spine.get("design_candidate"):
        recurrent_gap_types.append("design_proof_incomplete")
    if signal_count < 3:
        recurrent_gap_types.append("evidence_coverage_low")

    pattern_stability = min(1.0, route_counts.get(current_route, 0) / max(1, len(records)))
    signal_noise_ratio = min(1.0, signal_count / max(1, signal_count + len(recurrent_gap_types) * 2))
    gap_closure_rate = 1.0 if not recurrent_gap_types else max(0.25, 1.0 - len(recurrent_gap_types) * 0.18)
    adaptive_route_credit = (
        0.72
        if pattern_stability < 0.72
        and not recurrent_gap_types
        and design_proof_ready
        and signal_count >= 5
        else pattern_stability
    )
    quality_score = round(
        (adaptive_route_credit * 0.24)
        + (signal_noise_ratio * 0.24)
        + (gap_closure_rate * 0.22)
        + (0.16 if design_proof_ready else 0.06)
        + (0.14 if quality_gate.get("lifecycle_memory_written") else 0.04),
        4,
    )

    return {
        "schema_version": "claire.recursive_learning_snapshot.v1",
        "status": "recursive_learning_ready" if quality_score >= 0.70 else "recursive_learning_needs_more_runs",
        "source": "governed_lifecycle_memory",
        "documents_used_as_runtime_programming": False,
        "run_count": len(records),
        "current_run_id": run_spine.get("run_id"),
        "current_route": current_route,
        "learning_signal_extraction": {
            "signal_count": signal_count,
            "current_keywords": current_keywords[:12],
            "recurring_keywords": recurring_keywords,
        },
        "run_pattern_mining": {
            "route_counts": dict(route_counts),
            "dominant_route": route_counts.most_common(1)[0][0] if route_counts else current_route,
            "pattern_stability": round(pattern_stability, 4),
            "adaptive_route_credit": round(adaptive_route_credit, 4),
        },
        "recurring_gap_detection": {
            "gaps": recurrent_gap_types,
            "gap_closure_rate": round(gap_closure_rate, 4),
            "remediation": "increase evidence quality, design proof depth, or acquirer fit evidence" if recurrent_gap_types else "no recurring runtime gaps detected in current memory window",
        },
        "thesis_evolution": {
            "latest_thesis": run_spine.get("thesis", {}).get("statement"),
            "portfolio_title": run_spine.get("portfolio_candidate", {}).get("title"),
            "route_changed_from_previous": len(route_counts) > 1,
        },
        "emergence_learning": {
            "status": "bound" if emergence else "waiting_for_emergence_engine",
            "readiness_score": emergence.get("readiness_score"),
            "product_completion_percent": emergence.get("product_completion_percent"),
            "cycle_stage": emergence.get("cycle_stage"),
            "detected_patterns": emergence.get("detected_patterns", []),
            "ready_signal_families": emergence.get("ready_signal_families", []),
            "next_pattern_action": (
                "compare next cycle against detected patterns and signal family movement"
                if emergence
                else "attach system emergence engine to current run"
            ),
        },
        "recursive_quality": {
            "score": quality_score,
            "signal_noise_ratio": round(signal_noise_ratio, 4),
            "memory_feedback_eligible": quality_score >= 0.70,
            "regression_detected": quality_score < 0.58,
        },
        "strategy_memory": {
            "status": "updated",
            "focus_keywords": [item["keyword"] for item in recurring_keywords[:5]] or current_keywords[:5],
            "next_learning_action": "compare next scheduled cycle against this route and proof score",
        },
        "operator_review_required": True,
    }
