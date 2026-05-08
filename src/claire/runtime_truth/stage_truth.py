from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

from .runtime_truth_contract import LIFECYCLE_STAGES, ROUTE_REQUIRED_STAGES, coerce_list, first_present, normalize_route, normalize_stage_status, stage_domain, stage_name


@dataclass
class StageTruth:
    stage_number: int
    stage_name: str
    domain: str
    status: str
    started_at: str
    completed_at: str
    duration_ms: int | None
    route_applicability: str
    skip_reason: str
    confidence: float | None
    evidence_count: int
    output_summary: str
    error: str
    critical_design_stage: bool
    required_for_selected_route: bool
    raw: Any


def _stage_number(value: Any) -> Optional[int]:
    if isinstance(value, int):
        return value if 1 <= value <= 30 else None
    if isinstance(value, str):
        text = value.lower().replace("stage_", "")
        digits = "".join(ch for ch in text if ch.isdigit())
        if digits:
            number = int(digits)
            return number if 1 <= number <= 30 else None
    if isinstance(value, Mapping):
        return _stage_number(first_present(value, ["stage_number", "number", "stage", "id", "stage_id"], None))
    return None


def _summary(value: Any) -> str:
    if isinstance(value, Mapping):
        return str(first_present(value, ["output_summary", "summary", "result_summary", "description", "reason", "status_message"], ""))[:500]
    if isinstance(value, str):
        return value[:500]
    return ""


def _confidence(value: Any) -> float | None:
    if isinstance(value, Mapping):
        value = first_present(value, ["confidence", "score", "confidence_score"], None)
    try:
        if value is None or value == "":
            return None
        score = float(value)
        return max(0.0, min(1.0, score if score <= 1 else score / 100.0))
    except Exception:
        return None


def _evidence_count(value: Any) -> int:
    if isinstance(value, Mapping):
        evidence = first_present(value, ["evidence", "evidence_chain", "sources", "citations"], None)
        if evidence is None:
            return 0
        return len(coerce_list(evidence))
    return 0


def _duration(value: Any) -> int | None:
    if not isinstance(value, Mapping):
        return None
    raw = first_present(value, ["duration_ms", "duration", "elapsed_ms"], None)
    try:
        if raw is None or raw == "":
            return None
        return int(float(raw))
    except Exception:
        return None


def _collect_stage_candidates(raw: Mapping[str, Any]) -> Dict[int, Any]:
    stage_map: Dict[int, Any] = {}
    containers = [
        raw.get("lifecycle_stages"),
        raw.get("stages"),
        raw.get("core_lifecycle_stages"),
        raw.get("stage_outputs"),
        raw.get("stage_results"),
        raw.get("stage_truth"),
    ]
    summary = raw.get("core_lifecycle_summary")
    if isinstance(summary, Mapping):
        containers.extend([summary.get("stages_completed"), summary.get("stages_skipped"), summary.get("stages_failed")])
    for container in containers:
        if isinstance(container, Mapping):
            for key, value in container.items():
                number = _stage_number(value) or _stage_number(key)
                if number:
                    stage_map[number] = value
        elif isinstance(container, list):
            for value in container:
                number = _stage_number(value)
                if number:
                    stage_map[number] = value
    # Also support simple lists such as stages_completed=[1,2,3]
    status_lists = [("stages_completed", "completed"), ("completed_stages", "completed"), ("stages_skipped", "skipped_by_route"), ("skipped_stages", "skipped_by_route"), ("stages_failed", "failed"), ("failed_stages", "failed"), ("stages_blocked", "blocked"), ("blocked_stages", "blocked")]
    for key, status in status_lists:
        items = raw.get(key)
        if isinstance(items, Mapping):
            items = list(items.values())
        for item in coerce_list(items):
            number = _stage_number(item)
            if number and number not in stage_map:
                stage_map[number] = {"stage_number": number, "status": status, "summary": f"Reported through {key}"}
    return stage_map


def build_stage_truth(raw: Mapping[str, Any], selected_route: str) -> List[Dict[str, Any]]:
    route = normalize_route(selected_route)
    required = set(ROUTE_REQUIRED_STAGES.get(route, []))
    stage_map = _collect_stage_candidates(raw)
    results: List[Dict[str, Any]] = []
    for stage in LIFECYCLE_STAGES:
        number = int(stage["number"])
        item = stage_map.get(number)
        required_for_route = number in required or not route or route == "not_reported"
        if item is None:
            if route and route != "not_reported" and not required_for_route:
                status = "not_applicable"
                skip_reason = "not required for selected route"
                applicability = "not_applicable"
                summary = "Stage is outside the selected route contract."
            elif route and route != "not_reported":
                status = "blocked"
                skip_reason = "required stage truth was not reported"
                applicability = "required_missing_truth"
                summary = "Required stage has no reported runtime truth."
            else:
                status = "pending"
                skip_reason = "route not selected or no stage truth reported"
                applicability = "unknown_until_route_selected"
                summary = "Stage truth is not available yet."
            item = {}
        else:
            status = normalize_stage_status(first_present(item, ["status", "state", "result"], None) if isinstance(item, Mapping) else item, default="pending")
            skip_reason = str(first_present(item, ["skip_reason", "reason_if_skipped", "reason"], "") if isinstance(item, Mapping) else "")
            applicability = "required" if required_for_route else "reported_outside_selected_route"
            summary = _summary(item)
        error = str(first_present(item, ["error", "exception", "failure_reason"], "") if isinstance(item, Mapping) else "")
        truth = StageTruth(
            stage_number=number,
            stage_name=str(stage["name"]),
            domain=stage_domain(number),
            status=status,
            started_at=str(first_present(item, ["started_at", "start_time"], "not_reported") if isinstance(item, Mapping) else "not_reported"),
            completed_at=str(first_present(item, ["completed_at", "end_time", "finished_at"], "not_reported") if isinstance(item, Mapping) else "not_reported"),
            duration_ms=_duration(item),
            route_applicability=applicability,
            skip_reason=skip_reason,
            confidence=_confidence(item),
            evidence_count=_evidence_count(item),
            output_summary=summary,
            error=error,
            critical_design_stage=16 <= number <= 22,
            required_for_selected_route=required_for_route,
            raw=item,
        )
        results.append(asdict(truth))
    return results
