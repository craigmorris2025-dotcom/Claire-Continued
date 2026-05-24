from __future__ import annotations

from typing import Any, Dict, List


DEGRADED_VALUES = {"degraded", "stale", "offline", "unavailable", "failed", "blocked", "unknown"}
RECOVERY_VALUES = {"connected", "available", "fresh", "active", "complete", "healthy", "ready", "stable"}


def classify_timeline_event(event: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(event) if isinstance(event, dict) else {}
    event_type = str(item.get("type", "unknown"))
    field = str(item.get("field", "unknown"))
    from_value = str(item.get("from", "unknown")).lower()
    to_value = str(item.get("to", "unknown")).lower()

    classification = "observability"
    severity = "info"

    if "governance" in event_type or field == "runtime_authority":
        classification = "governance"
        severity = "guarded"
    elif "heartbeat" in event_type:
        classification = "heartbeat"
        severity = "info"
    elif "freshness" in event_type or field == "freshness":
        classification = "payload_freshness"
        severity = "warning" if to_value in DEGRADED_VALUES else "info"
    elif "synchronization" in event_type or field == "connection_state":
        classification = "synchronization"
        severity = "warning" if to_value in DEGRADED_VALUES else "info"
    elif "transition" in event_type or field in {"route", "terminal_state"}:
        classification = "runtime_transition"
        severity = "info"

    if to_value in DEGRADED_VALUES and from_value not in DEGRADED_VALUES:
        classification = "route_degradation"
        severity = "warning"
    elif from_value in DEGRADED_VALUES and to_value in RECOVERY_VALUES:
        classification = "route_recovery"
        severity = "recovered"

    item["classification"] = classification
    item["severity"] = severity
    item["presentation_only"] = True
    item["runtime_authority"] = "blocked"
    return item


def classify_timeline(timeline: Dict[str, Any]) -> Dict[str, Any]:
    timeline = dict(timeline) if isinstance(timeline, dict) else {}
    events = timeline.get("events") if isinstance(timeline.get("events"), list) else []
    classified_events: List[Dict[str, Any]] = [classify_timeline_event(event) for event in events]

    summary = timeline.get("summary") if isinstance(timeline.get("summary"), dict) else {}
    counts: Dict[str, int] = {}
    for event in classified_events:
        key = str(event.get("classification", "observability"))
        counts[key] = counts.get(key, 0) + 1

    timeline["events"] = classified_events
    timeline["classification_summary"] = {
        "version": "v19.89.8-S15",
        "event_total": len(classified_events),
        "counts": counts,
        "last_route": summary.get("last_route", "unknown"),
        "last_terminal_state": summary.get("last_terminal_state", "unknown"),
        "runtime_authority": "blocked",
        "presentation_only": True,
        "autonomous_execution_expansion": False,
    }

    authority = timeline.get("authority") if isinstance(timeline.get("authority"), dict) else {}
    authority["runtime_authority"] = "blocked"
    authority["cockpit_presentation_only"] = True
    authority["autonomous_execution_expansion"] = False
    timeline["authority"] = authority
    return timeline


def attach_timeline_classification(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(payload) if isinstance(payload, dict) else {}
    timeline = payload.get("governed_runtime_timeline")
    if isinstance(timeline, dict):
        payload["governed_runtime_timeline"] = classify_timeline(timeline)
    return payload
