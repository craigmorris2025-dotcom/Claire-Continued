from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from .runtime_truth_contract import coerce_list, first_present, normalize_route


@dataclass
class EvidenceTruth:
    evidence_id: str
    source: str
    source_type: str
    stage_number: int | None
    route: str
    claim_supported: str
    confidence: float | None
    timestamp: str
    trace_reference: str
    raw: Any


def _confidence(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        score = float(value)
        return max(0.0, min(1.0, score if score <= 1 else score / 100.0))
    except Exception:
        return None


def _stage(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        text = str(value).lower().replace("stage_", "")
        digits = "".join(ch for ch in text if ch.isdigit())
        number = int(digits) if digits else int(value)
        return number if 1 <= number <= 30 else None
    except Exception:
        return None


def _raw_evidence(raw: Mapping[str, Any]) -> List[Any]:
    for key in ["evidence_chain", "evidence", "sources", "citations", "traceability", "evidence_basket"]:
        if key in raw:
            return coerce_list(raw.get(key))
    return []


def build_evidence_truth(raw: Mapping[str, Any], selected_route: str) -> List[Dict[str, Any]]:
    items = _raw_evidence(raw)
    results: List[Dict[str, Any]] = []
    route = normalize_route(selected_route) or "not_reported"
    for idx, item in enumerate(items, start=1):
        if isinstance(item, Mapping):
            evidence_id = str(first_present(item, ["evidence_id", "id", "trace_id"], f"evidence_{idx:03d}"))
            source = str(first_present(item, ["source", "url", "title", "name", "path"], "not_reported"))
            source_type = str(first_present(item, ["source_type", "type", "kind"], "not_reported"))
            stage_number = _stage(first_present(item, ["stage_number", "stage", "stage_id"], None))
            claim = str(first_present(item, ["claim_supported", "claim", "summary", "description"], "not_reported"))
            confidence = _confidence(first_present(item, ["confidence", "score"], None))
            timestamp = str(first_present(item, ["timestamp", "created_at", "observed_at"], "not_reported"))
            trace = str(first_present(item, ["trace_reference", "reference", "citation", "pointer"], "not_reported"))
            item_route = normalize_route(first_present(item, ["route"], route)) or route
        else:
            evidence_id = f"evidence_{idx:03d}"
            source = str(item)
            source_type = "raw"
            stage_number = None
            claim = str(item)[:250]
            confidence = None
            timestamp = "not_reported"
            trace = "not_reported"
            item_route = route
        results.append(asdict(EvidenceTruth(evidence_id, source, source_type, stage_number, item_route, claim, confidence, timestamp, trace, item)))
    return results
