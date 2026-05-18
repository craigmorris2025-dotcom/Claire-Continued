from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


EVIDENCE_BASKET_VERSION = "v19.89.8-S22"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _collect_evidence_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    event_stream = payload.get("event_stream")
    if isinstance(event_stream, dict) and isinstance(event_stream.get("events"), list):
        for index, event in enumerate(event_stream["events"][-8:]):
            if isinstance(event, dict):
                items.append({
                    "id": event.get("id") or f"event:{index}",
                    "kind": "runtime_event",
                    "title": event.get("type") or "Runtime Event",
                    "status": event.get("status", "observed"),
                    "trust_state": "runtime_observed",
                    "promotion_state": "review_required",
                    "runtime_authority": "blocked",
                })

    timeline = payload.get("governed_runtime_timeline")
    if isinstance(timeline, dict) and isinstance(timeline.get("events"), list):
        for index, event in enumerate(timeline["events"][-8:]):
            if isinstance(event, dict):
                items.append({
                    "id": event.get("id") or f"timeline:{index}",
                    "kind": "timeline_event",
                    "title": event.get("classification") or event.get("type") or "Timeline Event",
                    "status": event.get("severity", "info"),
                    "trust_state": "timeline_observed",
                    "promotion_state": "review_required",
                    "runtime_authority": "blocked",
                })

    return items[-24:]


def build_evidence_basket(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    items = _collect_evidence_items(payload)

    counts: Dict[str, int] = {}
    for item in items:
        kind = str(item.get("kind", "unknown"))
        counts[kind] = counts.get(kind, 0) + 1

    return {
        "version": EVIDENCE_BASKET_VERSION,
        "status": "active",
        "observed_at_utc": _utc_now(),
        "authority": {
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "runtime_authority": "blocked",
            "fail_closed_governance": True,
            "autonomous_execution_expansion": False,
            "evidence_promotion": "manual_review_required",
        },
        "summary": {
            "evidence_total": len(items),
            "kind_counts": counts,
            "promotion_ready": False,
            "manual_review_required": True,
            "automatic_truth_mutation": False,
        },
        "items": items,
    }


def attach_evidence_basket(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    payload["governed_evidence_basket"] = build_evidence_basket(payload)
    return payload
