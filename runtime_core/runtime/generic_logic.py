"""Governed deterministic logic for formerly throw-only modules."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def summarize_context(context: Any) -> dict[str, Any]:
    text = str(context or "")
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    keywords = sorted(counts, key=lambda item: (-counts[item], item))[:12]
    return {
        "text_length": len(text),
        "keyword_count": len(keywords),
        "keywords": keywords,
        "digest": sha256(text[:4000].encode("utf-8")).hexdigest()[:16],
    }


def governed_result(module: str, operation: str, context: Any = None, *, spec: str = "") -> dict[str, Any]:
    summary = summarize_context(context)
    confidence = round(min(0.9, 0.4 + summary["keyword_count"] * 0.03), 4)
    return {
        "schema_version": "claire.governed_generic_result.v1",
        "module": module,
        "operation": operation,
        "status": "ready_for_review" if summary["keyword_count"] else "needs_input",
        "generated_at": now(),
        "summary": summary,
        "spec": spec,
        "confidence": confidence,
        "recommendations": build_recommendations(operation, summary["keywords"]),
        "evidence": [
            {
                "evidence_id": f"{operation}-{summary['digest']}",
                "type": "local_context_analysis",
                "metadata_only": True,
                "body_read_performed": False,
                "runtime_truth_write": "blocked",
            }
        ],
        "manual_review_required": True,
        "automatic_update_performed": False,
        "autonomous_execution_performed": False,
        "runtime_truth_mutation": False,
    }


def build_recommendations(operation: str, keywords: list[str]) -> list[dict[str, Any]]:
    if not keywords:
        return [{"action": "provide_context", "priority": "high"}]
    return [
        {"action": f"review_{operation}", "priority": "high", "basis_terms": keywords[:5]},
        {"action": "validate_with_tests_or_operator_evidence", "priority": "medium"},
    ]


def validate_governed_result(result: dict[str, Any]) -> bool:
    return (
        isinstance(result, dict)
        and result.get("schema_version") == "claire.governed_generic_result.v1"
        and result.get("runtime_truth_mutation") is False
        and result.get("autonomous_execution_performed") is False
    )
