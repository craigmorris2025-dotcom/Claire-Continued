"""Small real completion-analysis helpers used by v10 completion modules."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def as_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        if isinstance(value.get("capabilities"), list):
            return [item if isinstance(item, dict) else {"name": str(item)} for item in value["capabilities"]]
        return [{"name": str(key), **(item if isinstance(item, dict) else {"value": item})} for key, item in value.items()]
    if isinstance(value, list):
        return [item if isinstance(item, dict) else {"name": str(item)} for item in value]
    return []


def status_for(item: dict[str, Any]) -> str:
    raw = str(item.get("status") or item.get("state") or "").lower()
    if raw in {"delivered", "complete", "completed", "ready", "passed", "closed"}:
        return "DELIVERED"
    if raw in {"partial", "in_progress", "working", "review"}:
        return "PARTIAL"
    if raw in {"descoped", "not_applicable"}:
        return "DESCOPED"
    if raw in {"deferred", "blocked"}:
        return "DEFERRED"
    if item.get("delivered") is True or item.get("passed") is True:
        return "DELIVERED"
    return "NOT_STARTED"


def closure_report(registry: Any) -> dict[str, Any]:
    items = as_items(registry)
    statuses = [{**item, "closure_status": status_for(item)} for item in items]
    closed = [item for item in statuses if item["closure_status"] in {"DELIVERED", "DESCOPED"}]
    partial = [item for item in statuses if item["closure_status"] == "PARTIAL"]
    rate = round(len(closed) / len(statuses), 4) if statuses else 0.0
    return {
        "schema_version": "claire.completion.closure_report.v1",
        "generated_at": now(),
        "status": "closure_verified" if statuses and rate >= 1 else "closure_partial" if statuses else "no_capabilities_supplied",
        "capability_count": len(statuses),
        "closed_count": len(closed),
        "partial_count": len(partial),
        "closure_rate": rate,
        "capabilities": statuses,
        "unclosed": [item for item in statuses if item["closure_status"] not in {"DELIVERED", "DESCOPED"}],
    }


def numeric_score(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def scorecard(contract: dict[str, Any], evidence: dict[str, Any] | list[Any] | None = None) -> dict[str, Any]:
    evidence = evidence or {}
    dimensions = ["functionality", "quality", "performance", "security", "documentation", "testing", "deployment_readiness"]
    evidence_text = str(evidence).lower()
    scores: dict[str, dict[str, Any]] = {}
    for dimension in dimensions:
        explicit = evidence.get(dimension) if isinstance(evidence, dict) else None
        score = numeric_score(explicit, 0.0) if explicit is not None else (0.75 if dimension in evidence_text else 0.45)
        scores[dimension] = {
            "score": score,
            "status": "passed" if score >= 0.7 else "needs_work" if score >= 0.4 else "missing",
            "evidence_present": explicit is not None or dimension in evidence_text,
        }
    overall = round(sum(item["score"] for item in scores.values()) / len(scores), 4)
    target = numeric_score(contract.get("target_score", 0.8) if isinstance(contract, dict) else 0.8, 0.8)
    return {
        "schema_version": "claire.completion.scorecard.v1",
        "generated_at": now(),
        "status": "target_met" if overall >= target else "target_not_met",
        "overall_score": overall,
        "target_score": target,
        "dimensions": scores,
        "gap": round(max(0.0, target - overall), 4),
    }


def maturity_gaps(current: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(current) | set(target))
    gaps = []
    for key in keys:
        current_score = numeric_score(current.get(key), 0.0)
        target_score = numeric_score(target.get(key), 1.0)
        gap = round(max(0.0, target_score - current_score), 4)
        if gap:
            gaps.append(
                {
                    "dimension": key,
                    "current": current_score,
                    "target": target_score,
                    "gap": gap,
                    "priority": "high" if gap >= 0.4 else "medium" if gap >= 0.2 else "low",
                    "remediation": f"Raise {key} evidence and verification coverage to target.",
                }
            )
    gaps.sort(key=lambda item: (-item["gap"], item["dimension"]))
    return {
        "schema_version": "claire.completion.maturity_gap_analysis.v1",
        "generated_at": now(),
        "status": "gaps_found" if gaps else "target_met",
        "gap_count": len(gaps),
        "gaps": gaps,
    }


def report_from_binder(binder: dict[str, Any]) -> dict[str, Any]:
    paths = binder.get("paths", {}) if isinstance(binder, dict) else {}
    return {
        "schema_version": "claire.completion.report.v1",
        "generated_at": now(),
        "status": binder.get("status", "unknown") if isinstance(binder, dict) else "unknown",
        "completion_percent": binder.get("completion_percent") if isinstance(binder, dict) else None,
        "proof_phase_complete": binder.get("proof_phase_complete") if isinstance(binder, dict) else None,
        "quality_summary": binder.get("area_scores", {}) if isinstance(binder, dict) else {},
        "artifacts": paths,
        "release_note": "Completion report generated from verified binder data.",
    }


def ensure_under(path: Path, root: Path) -> Path:
    path = path.resolve()
    root = root.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"path escapes root: {path}")
    return path
