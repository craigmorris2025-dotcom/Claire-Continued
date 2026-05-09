from __future__ import annotations

from typing import Any, Dict

from .evidence_traceability import build_evidence_traceability_index


def summarize_evidence(runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    index = build_evidence_traceability_index(runtime_truth)
    return {
        "evidence_count": index.get("evidence_count", 0),
        "unsupported_count": index.get("unsupported_count", 0),
        "stages_with_evidence": len(index.get("by_stage", {})),
        "routes_with_evidence": len(index.get("by_route", {})),
        "source_type_count": len(index.get("by_source_type", {})),
    }
