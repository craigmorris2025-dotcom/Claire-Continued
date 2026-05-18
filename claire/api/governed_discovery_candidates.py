from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping

TERMINAL_LOCKS = {
    "backend_owns_truth": True,
    "cockpit_presentation_only": True,
    "runtime_truth_mutation_blocked": True,
    "runtime_truth_write_blocked": True,
    "automatic_updates_blocked": True,
    "autonomous_execution_blocked": True,
    "live_web_execution_requires_explicit_gate": True,
    "manual_promotion_mandatory": True,
    "quarantine_mandatory": True,
    "continuous_crawling_blocked": True,
}

ROUTE_KEYWORDS = {
    "portfolio": ("stock", "equity", "portfolio", "market", "valuation", "earnings", "margin", "revenue", "yield", "risk", "asset", "sector"),
    "breakthrough": ("breakthrough", "novel", "patent", "invention", "emerging", "disruptive", "new capability", "research", "prototype"),
    "design": ("design", "architecture", "blueprint", "component", "build", "manufacturing", "deploy", "system", "stack", "engineering"),
}

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()[:16]}"

def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value)
    return [value]

def _collect_strings(value: Any) -> List[str]:
    found: List[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, Mapping):
        for item in value.values():
            found.extend(_collect_strings(item))
    elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            found.extend(_collect_strings(item))
    return found

def _infer_route(text: str, requested_route: str | None = None) -> str:
    if requested_route in {"portfolio", "breakthrough", "design"}:
        return requested_route
    lowered = text.lower()
    scores = {route: sum(1 for keyword in keywords if keyword in lowered) for route, keywords in ROUTE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "discovery"
    return best

def _extract_evidence_ids(evidence_basket: Mapping[str, Any]) -> List[str]:
    ids: List[str] = []
    for key in ("evidence_items", "items", "results", "sources"):
        for item in _as_list(evidence_basket.get(key)):
            if isinstance(item, Mapping):
                evidence_id = item.get("evidence_id") or item.get("id") or item.get("result_id")
                if evidence_id:
                    ids.append(str(evidence_id))
    if not ids and evidence_basket.get("evidence_id"):
        ids.append(str(evidence_basket["evidence_id"]))
    return sorted(set(ids))

def _collect_signals(extraction: Mapping[str, Any], evidence_basket: Mapping[str, Any]) -> List[Dict[str, Any]]:
    raw = []
    for key in ("signals", "extracted_signals", "entities", "entity_signals"):
        raw.extend(_as_list(extraction.get(key)))
    if not raw:
        for key in ("signals", "extracted_signals", "entities", "entity_signals"):
            raw.extend(_as_list(evidence_basket.get(key)))

    signals: List[Dict[str, Any]] = []
    for index, item in enumerate(raw):
        if isinstance(item, Mapping):
            label = item.get("label") or item.get("name") or item.get("entity") or item.get("signal")
            kind = item.get("kind") or item.get("type") or "signal"
            confidence = item.get("confidence", item.get("score", 0.5))
        else:
            label = str(item)
            kind = "signal"
            confidence = 0.5
        if label:
            signals.append({
                "signal_id": f"signal_{index + 1}",
                "label": str(label),
                "kind": str(kind),
                "confidence": float(confidence) if isinstance(confidence, (int, float)) else 0.5,
            })
    return signals

def _basket_trust(evidence_basket: Mapping[str, Any]) -> float:
    for key in ("trust_score", "source_trust_score", "lineage_trust_score"):
        value = evidence_basket.get(key)
        if isinstance(value, (int, float)):
            return round(max(0.0, min(1.0, float(value))), 4)
    summary = evidence_basket.get("summary")
    if isinstance(summary, Mapping):
        for key in ("trust_score", "average_trust_score"):
            value = summary.get(key)
            if isinstance(value, (int, float)):
                return round(max(0.0, min(1.0, float(value))), 4)
    return 0.5

def build_discovery_candidate(evidence_basket: Mapping[str, Any], extraction: Mapping[str, Any] | None = None, requested_route: str | None = None) -> Dict[str, Any]:
    extraction = extraction or {}
    strings = _collect_strings({"evidence": evidence_basket, "extraction": extraction})
    combined_text = " ".join(strings).strip()
    route = _infer_route(combined_text, requested_route)
    signals = _collect_signals(extraction, evidence_basket)
    evidence_ids = _extract_evidence_ids(evidence_basket)
    trust_score = _basket_trust(evidence_basket)
    signal_strength = min(1.0, len(signals) / 5.0)
    confidence = round((trust_score * 0.7) + (signal_strength * 0.3), 4)
    headline_seed = ""
    for item in signals:
        if item.get("label"):
            headline_seed = str(item["label"])
            break
    if not headline_seed:
        headline_seed = str(evidence_basket.get("headline") or extraction.get("headline") or "Governed evidence discovery candidate")
    base_payload = {"route": route, "evidence_ids": evidence_ids, "signals": signals, "headline_seed": headline_seed}
    return {
        "candidate_id": _stable_id("disc", base_payload),
        "candidate_version": "S85",
        "created_at": _utc_now(),
        "candidate_type": route,
        "status": "quarantined_candidate",
        "headline": f"{route.title()} candidate: {headline_seed}",
        "summary": "Structured discovery candidate generated from quarantined governed evidence. This is not runtime truth and requires manual operator review.",
        "source_evidence_ids": evidence_ids,
        "signals": signals,
        "confidence": confidence,
        "trust_score": trust_score,
        "governance": dict(TERMINAL_LOCKS),
        "authority": {
            "runtime_truth": "blocked",
            "runtime_truth_write": "blocked",
            "manual_review_required": True,
            "promotion_allowed": False,
            "quarantine_required": True,
        },
        "lineage": {
            "evidence_basket_id": evidence_basket.get("basket_id") or evidence_basket.get("id"),
            "extraction_id": extraction.get("extraction_id") or extraction.get("id"),
            "source": "governed_evidence_basket",
        },
    }

def build_route_discovery_candidates(evidence_basket: Mapping[str, Any], extraction: Mapping[str, Any] | None = None, routes: Iterable[str] = ("portfolio", "breakthrough", "design")) -> Dict[str, Dict[str, Any]]:
    return {route: build_discovery_candidate(evidence_basket, extraction, requested_route=route) for route in routes}
