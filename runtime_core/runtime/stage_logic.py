"""Deterministic fallback logic for legacy lifecycle stage modules.

These helpers turn the old generated stage shells into useful local processors.
They do not perform network access, body reads, autonomous actions, or runtime
truth writes.
"""

from __future__ import annotations

import re
from hashlib import sha256
from typing import Any


KEYWORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


def _flatten_text(value: Any, *, limit: int = 12000) -> str:
    parts: list[str] = []

    def visit(item: Any) -> None:
        if len(" ".join(parts)) >= limit:
            return
        if item is None:
            return
        if isinstance(item, (str, int, float, bool)):
            parts.append(str(item))
            return
        if isinstance(item, dict):
            for key, nested in item.items():
                parts.append(str(key))
                visit(nested)
            return
        if isinstance(item, (list, tuple, set)):
            for nested in item:
                visit(nested)

    visit(value)
    return " ".join(" ".join(parts).split())[:limit]


def _keywords(text: str, *, limit: int = 18) -> list[str]:
    stop = {
        "and",
        "are",
        "for",
        "from",
        "has",
        "into",
        "not",
        "that",
        "the",
        "this",
        "with",
    }
    counts: dict[str, int] = {}
    for token in KEYWORD_RE.findall(text.lower()):
        if token in stop:
            continue
        counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts, key=lambda token: (-counts[token], token))
    return ranked[:limit]


def _confidence(payload: dict[str, Any], keywords: list[str], evidence_count: int) -> float:
    base = 0.35
    if payload:
        base += 0.2
    base += min(0.25, len(keywords) * 0.015)
    base += min(0.2, evidence_count * 0.04)
    return round(max(0.0, min(0.92, base)), 4)


def _evidence(stage_id: int, stage_name: str, text: str, keywords: list[str]) -> list[dict[str, Any]]:
    digest = sha256(f"{stage_id}|{stage_name}|{text[:2000]}".encode("utf-8")).hexdigest()[:16]
    return [
        {
            "evidence_id": f"stage-{stage_id}-{digest}",
            "type": "local_input_analysis",
            "summary": f"{stage_name} processed {len(text)} characters of local stage input.",
            "keywords": keywords[:8],
            "metadata_only": True,
            "body_read_performed": False,
            "runtime_truth_write": "blocked",
        }
    ]


def _status_for(stage_key: str, keywords: list[str]) -> str:
    if not keywords:
        return f"{stage_key}_needs_input"
    return f"{stage_key}_ready"


def build_stage_payload(stage_id: int, stage_name: str, stage_input: dict[str, Any]) -> dict[str, Any]:
    payload = stage_input.get("payload", {}) if isinstance(stage_input, dict) else {}
    payload = payload if isinstance(payload, dict) else {"value": payload}
    text = _flatten_text({"payload": payload, "metadata": stage_input.get("metadata", {})})
    keywords = _keywords(text)
    evidence = _evidence(stage_id, stage_name, text, keywords)
    stage_key = re.sub(r"[^a-z0-9]+", "_", stage_name.lower()).strip("_") or f"stage_{stage_id}"
    confidence = _confidence(payload, keywords, len(evidence))

    result: dict[str, Any] = {
        "schema_version": "claire.stage_logic.v1",
        "stage_id": stage_id,
        "stage_name": stage_name,
        "status": _status_for(stage_key, keywords),
        "input_summary": {
            "source_stage": stage_input.get("source_stage"),
            "payload_keys": sorted(str(key) for key in payload.keys()),
            "metadata_keys": sorted(str(key) for key in (stage_input.get("metadata", {}) or {}).keys())
            if isinstance(stage_input.get("metadata", {}), dict)
            else [],
            "text_length": len(text),
        },
        "keywords": keywords,
        "signals": [{"term": term, "weight": round(1.0 - index * 0.03, 4)} for index, term in enumerate(keywords[:10])],
        "confidence": confidence,
        "evidence": evidence,
        "manual_review_required": True,
        "body_read_performed": False,
        "runtime_truth_write": "blocked",
        "automatic_update_performed": False,
    }

    if "portfolio" in stage_key:
        result["portfolio_decision"] = "review_candidate" if confidence >= 0.55 else "watchlist"
    if "acquisition" in stage_key or "package" in stage_key:
        result["package_sections"] = ["thesis", "evidence", "risks", "next_actions"]
    if "route" in stage_key or "path" in stage_key:
        result["route_selected"] = "breakthrough_design" if any(term in keywords for term in ("design", "build", "invention")) else "portfolio_creation_optimization"
    if "feasibility" in stage_key or "viability" in stage_key or "buildability" in stage_key:
        result["readiness"] = "ready_for_review" if confidence >= 0.55 else "needs_more_evidence"
    if "trend" in stage_key or "cluster" in stage_key:
        result["trend_terms"] = keywords[:6]
    if "entity" in stage_key:
        result["entities"] = [{"name": term, "type": "keyword_entity"} for term in keywords[:10]]
    if "relationship" in stage_key:
        result["relationships"] = [
            {"source": keywords[index], "target": keywords[index + 1], "relationship": "co_occurs"}
            for index in range(max(0, min(len(keywords) - 1, 8)))
        ]

    return result
