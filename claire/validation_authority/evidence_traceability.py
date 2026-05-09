from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _first_present(mapping: Dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return list(value.values())
    return [value]


def extract_evidence_items(runtime_truth: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize evidence from runtime truth or legacy core_run_output shapes."""
    evidence_truth = runtime_truth.get("evidence_truth") or {}
    raw_items: List[Any] = []

    for key in ("evidence", "evidence_chain", "items", "traceability"):
        raw_items.extend(_as_list(evidence_truth.get(key)))

    raw_items.extend(_as_list(runtime_truth.get("evidence_chain")))

    # Stage-local evidence is also accepted.
    stage_truth = runtime_truth.get("stage_truth") or {}
    stages = stage_truth.get("stages") or runtime_truth.get("stages") or []
    for stage in _as_list(stages):
        if isinstance(stage, dict):
            stage_number = _first_present(stage, ("stage_number", "number", "id"))
            for item in _as_list(stage.get("evidence") or stage.get("evidence_items")):
                if isinstance(item, dict):
                    enriched = dict(item)
                    enriched.setdefault("stage_number", stage_number)
                    raw_items.append(enriched)
                else:
                    raw_items.append({
                        "stage_number": stage_number,
                        "claim_supported": str(item),
                        "source": "stage_local",
                    })

    normalized: List[Dict[str, Any]] = []
    seen = set()

    for index, item in enumerate(raw_items, start=1):
        if isinstance(item, str):
            item = {
                "claim_supported": item,
                "source": "unknown",
                "source_type": "text",
            }
        if not isinstance(item, dict):
            continue

        stage_number = _first_present(item, ("stage_number", "stage", "stage_id"))
        try:
            if isinstance(stage_number, str) and stage_number.strip().isdigit():
                stage_number = int(stage_number.strip())
        except Exception:
            pass

        evidence_id = _first_present(item, ("evidence_id", "id", "trace_id"))
        if not evidence_id:
            evidence_id = f"ev-{index:04d}"

        source = _first_present(item, ("source", "url", "document", "file", "reference"), "unknown")
        source_type = _first_present(item, ("source_type", "type", "kind"), "unknown")
        claim = _first_present(item, ("claim_supported", "claim", "summary", "text", "note"), "")
        confidence = _first_present(item, ("confidence", "score", "weight"), None)
        route = _first_present(item, ("route", "route_selected"), runtime_truth.get("route_selected"))

        dedupe_key = (str(evidence_id), str(stage_number), str(source), str(claim))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        normalized.append({
            "evidence_id": str(evidence_id),
            "stage_number": stage_number,
            "route": route or "unknown",
            "source": source,
            "source_type": source_type,
            "claim_supported": claim,
            "confidence": confidence,
            "timestamp": _first_present(item, ("timestamp", "created_at", "observed_at"), None),
            "trace_reference": _first_present(item, ("trace_reference", "trace", "path", "pointer"), None),
            "supported": bool(claim),
        })

    return normalized


def build_evidence_traceability_index(runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    items = extract_evidence_items(runtime_truth)

    by_stage: Dict[str, List[str]] = defaultdict(list)
    by_route: Dict[str, List[str]] = defaultdict(list)
    by_source_type: Dict[str, int] = defaultdict(int)
    unsupported: List[str] = []

    for item in items:
        evidence_id = item["evidence_id"]
        stage_key = str(item.get("stage_number") or "unknown")
        route_key = str(item.get("route") or "unknown")
        source_type = str(item.get("source_type") or "unknown")

        by_stage[stage_key].append(evidence_id)
        by_route[route_key].append(evidence_id)
        by_source_type[source_type] += 1

        if not item.get("supported"):
            unsupported.append(evidence_id)

    return {
        "schema": "claire.evidence_traceability_index.v1",
        "generated_at": utc_now(),
        "evidence_count": len(items),
        "unsupported_count": len(unsupported),
        "unsupported_evidence_ids": unsupported,
        "by_stage": dict(sorted(by_stage.items(), key=lambda kv: kv[0])),
        "by_route": dict(sorted(by_route.items(), key=lambda kv: kv[0])),
        "by_source_type": dict(sorted(by_source_type.items(), key=lambda kv: kv[0])),
        "items": items,
    }
