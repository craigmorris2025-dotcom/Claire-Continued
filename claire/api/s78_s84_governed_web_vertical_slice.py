from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

VERSION = "v19.89.8-S78-S84"

def authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }

def s78_provider_adapter_check() -> dict[str, Any]:
    env = {
        "google_cse_configured": bool(os.environ.get("GOOGLE_CSE_ID") and os.environ.get("GOOGLE_API_KEY")),
        "serpapi_configured": bool(os.environ.get("SERPAPI_API_KEY")),
        "brave_configured": bool(os.environ.get("BRAVE_SEARCH_API_KEY")),
        "provider_override": os.environ.get("CLAIRE_SEARCH_PROVIDER", "").strip() or None,
    }
    configured = any(v is True for v in env.values() if isinstance(v, bool))
    return {
        "version": VERSION,
        "stage": "S78",
        "status": "provider_adapter_check_ready",
        "configured_provider_available": configured,
        "provider_env": env,
        "adapter_state": "configured" if configured else "not_configured",
        "safe_to_probe": configured,
        "network_request_performed": False,
        **authority(),
    }

def s79_manual_operator_probe_request(query: str = "Claire governed web probe readiness") -> dict[str, Any]:
    return {
        "version": VERSION,
        "stage": "S79",
        "status": "manual_operator_probe_request_ready",
        "query": query,
        "provider_state": s78_provider_adapter_check()["adapter_state"],
        "metadata_only": True,
        "body_read_allowed": False,
        "operator_ack_required": True,
        "execution_state": "not_executed",
        "dry_run_available": True,
        "network_request_performed": False,
        **authority(),
    }

def s79_probe_dry_run(query: str = "Claire governed web probe readiness") -> dict[str, Any]:
    return {
        "version": VERSION,
        "stage": "S79",
        "status": "manual_operator_probe_dry_run_ready",
        "dry_run": True,
        "request": s79_manual_operator_probe_request(query),
        "would_execute_network": False,
        "result_shape": {"title": "string", "url": "string", "snippet": "string", "provider": "string"},
        "network_request_performed": False,
        **authority(),
    }

def s80_quarantined_result(result: dict[str, Any] | None = None) -> dict[str, Any]:
    result = result or {
        "title": "Sample quarantined provider result",
        "url": "https://example.com/sample",
        "snippet": "Placeholder result shape for quarantine storage contract.",
        "provider": "dry_run",
    }
    return {
        "version": VERSION,
        "stage": "S80",
        "status": "quarantined_probe_result_ready",
        "quarantine_id": "s80-quarantine-sample",
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "quarantine_state": "quarantined",
        "manual_review_required": True,
        "auto_promotion_enabled": False,
        **authority(),
    }

def s81_evidence_basket() -> dict[str, Any]:
    q = s80_quarantined_result()
    item = {
        "evidence_id": "s81-evidence-sample",
        "quarantine_id": q["quarantine_id"],
        "title": q["result"]["title"],
        "url": q["result"]["url"],
        "snippet": q["result"]["snippet"],
        "provider": q["result"]["provider"],
        "evidence_state": "quarantined",
        "promoted_to_runtime_truth": False,
        "runtime_truth_write_allowed": False,
    }
    return {
        "version": VERSION,
        "stage": "S81",
        "status": "evidence_basket_created",
        "basket_id": "s81-basket-sample",
        "evidence_count": 1,
        "evidence_items": [item],
        "auto_promotion_enabled": False,
        **authority(),
    }

def s82_source_lineage_trust_scoring() -> dict[str, Any]:
    basket = s81_evidence_basket()
    lineage = []
    for item in basket["evidence_items"]:
        domain = urlparse(item["url"]).netloc or "unknown"
        trust_score = 0.85 if domain.endswith(".gov") or domain.endswith(".edu") else 0.40 if domain == "example.com" else 0.50
        lineage.append({
            "lineage_id": f"s82-lineage-{item['evidence_id']}",
            "evidence_id": item["evidence_id"],
            "url": item["url"],
            "domain": domain,
            "provider": item["provider"],
            "trust_score": trust_score,
            "trust_band": "review_required",
            "requires_operator_review": True,
            "promoted_to_runtime_truth": False,
            "runtime_truth_write_allowed": False,
        })
    return {"version": VERSION, "stage": "S82", "status": "source_lineage_trust_scoring_ready", "lineage_count": len(lineage), "lineage": lineage, **authority()}

def _terms(text: str) -> list[str]:
    found = re.findall(r"[A-Za-z][A-Za-z0-9\\-]{3,}", text)
    out = []
    for t in found:
        n = t.lower()
        if n not in out:
            out.append(n)
    return out[:8]

def s83_entity_signal_extraction() -> dict[str, Any]:
    candidates = []
    for item in s81_evidence_basket()["evidence_items"]:
        candidates.append({
            "candidate_id": f"s83-candidate-{item['evidence_id']}",
            "evidence_id": item["evidence_id"],
            "entities": _terms(item["title"] + " " + item["snippet"]),
            "signal_type": "web_research_candidate",
            "signal_state": "candidate_requires_review",
            "confidence": "unscored_pending_review",
            "promoted_to_runtime_truth": False,
            "runtime_truth_write_allowed": False,
        })
    return {"version": VERSION, "stage": "S83", "status": "entity_signal_extraction_ready", "candidate_count": len(candidates), "candidates": candidates, **authority()}

def s84_dashboard_evidence_card() -> dict[str, Any]:
    basket = s81_evidence_basket()
    lineage = s82_source_lineage_trust_scoring()["lineage"]
    extraction = s83_entity_signal_extraction()["candidates"]
    cards = []
    for item in basket["evidence_items"]:
        line = next((x for x in lineage if x["evidence_id"] == item["evidence_id"]), {})
        candidate = next((x for x in extraction if x["evidence_id"] == item["evidence_id"]), {})
        cards.append({
            "card_id": f"s84-card-{item['evidence_id']}",
            "title": item["title"],
            "url": item["url"],
            "snippet": item["snippet"],
            "quarantine_state": item["evidence_state"],
            "domain": line.get("domain"),
            "trust_score": line.get("trust_score"),
            "entities": candidate.get("entities", []),
            "visible_to_operator": True,
            "runtime_truth_write_allowed": False,
            "promoted_to_runtime_truth": False,
        })
    return {"version": VERSION, "stage": "S84", "status": "dashboard_evidence_card_ready", "card_count": len(cards), "cards": cards, **authority()}

def verify_s78_s84_vertical_slice() -> dict[str, Any]:
    failures: list[str] = []
    dry = s79_probe_dry_run()
    if dry["would_execute_network"] or dry["network_request_performed"]:
        failures.append("dry run executed network")
    q = s80_quarantined_result()
    if q["quarantine_state"] != "quarantined":
        failures.append("result not quarantined")
    basket = s81_evidence_basket()
    if basket["evidence_count"] < 1:
        failures.append("no evidence")
    for item in basket["evidence_items"]:
        if item["promoted_to_runtime_truth"] or item["runtime_truth_write_allowed"]:
            failures.append(item["evidence_id"] + " truth write/promotion drift")
    cards = s84_dashboard_evidence_card()
    if cards["card_count"] < 1:
        failures.append("no dashboard evidence card")
    for card in cards["cards"]:
        if not card["visible_to_operator"]:
            failures.append(card["card_id"] + " not visible")
        if not card["entities"]:
            failures.append(card["card_id"] + " no extracted entities")
    return {"version": VERSION, "verification_ok": failures == [], "failures": failures, **authority()}

def build_s78_s84_plateau_report() -> dict[str, Any]:
    verification = verify_s78_s84_vertical_slice()
    return {
        "version": VERSION,
        "status": "s78_s84_ready" if verification["verification_ok"] else "s78_s84_blocked",
        "ready": verification["verification_ok"],
        "s78_provider_check": s78_provider_adapter_check(),
        "s79_probe": s79_probe_dry_run(),
        "s80_quarantine": s80_quarantined_result(),
        "s81_evidence_basket": s81_evidence_basket(),
        "s82_lineage": s82_source_lineage_trust_scoring(),
        "s83_extraction": s83_entity_signal_extraction(),
        "s84_dashboard_card": s84_dashboard_evidence_card(),
        "verification": verification,
        **authority(),
        "next_phase": "S85 discovery candidate from evidence",
    }

# --- v19.89.8 recovery: S32R2R1 live_web_execution_enabled exact safety contract ---
# Normalizes S32R2R1 web-safety payloads so the dashboard/test payload exposes
# live_web_execution_enabled == False instead of omitting the key.

def _v19898_s32r2r1_safety_keys():
    return {
        "live_web_execution_enabled": False,
        "web_execution_enabled": False,
        "browser_execution_enabled": False,
        "live_browser_execution_enabled": False,
        "runtime_mutation_enabled": False,
        "runtime_truth_write_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "body_read_allowed": False,
        "body_read_enabled": False,
        "self_apply_enabled": False,
        "live_web_execution_status": "blocked",
        "web_execution_status": "blocked",
        "browser_execution_status": "blocked",
        "governance_status": "locked",
    }


def _v19898_s32r2r1_normalize_payload(payload):
    if isinstance(payload, dict):
        for _key, _value in _v19898_s32r2r1_safety_keys().items():
            payload.setdefault(_key, _value)

        payload.setdefault("backend_owns_truth", True)
        payload.setdefault("cockpit_presentation_only", True)
        payload.setdefault("runtime_truth_write", "blocked")
        payload.setdefault("runtime_truth_modified", False)

        for _nested_key in [
            "governed_web_safety_activation",
            "web_safety_activation",
            "safety_activation",
            "blocked_authority_modes",
            "authority_locks",
            "internet_update_readiness",
        ]:
            _nested = payload.get(_nested_key)
            if isinstance(_nested, dict):
                for _key, _value in _v19898_s32r2r1_safety_keys().items():
                    _nested.setdefault(_key, _value)
                _nested.setdefault("backend_owns_truth", True)
                _nested.setdefault("cockpit_presentation_only", True)

        for _value in list(payload.values()):
            if isinstance(_value, dict):
                _v19898_s32r2r1_normalize_payload(_value)
            elif isinstance(_value, list):
                for _item in _value:
                    if isinstance(_item, dict):
                        _v19898_s32r2r1_normalize_payload(_item)
    return payload


def build_s32r2r1_web_safety_payload():
    return _v19898_s32r2r1_normalize_payload({
        "stage_version": "S32R2R1",
        "phase": "S32R2R1",
        "version": "v19.89.8-S32R2R1-live-web-execution-safety-contract",
        "status": "ok",
        "ok": True,
        "ready": True,
        "governed_web_safety_activation": {
            "status": "locked",
            "live_web_execution_enabled": False,
            "web_execution_enabled": False,
            "browser_execution_enabled": False,
            "runtime_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_crawling_enabled": False,
            "body_read_allowed": False,
        },
    })


def get_s32r2r1_web_safety_payload():
    return build_s32r2r1_web_safety_payload()


def build_s32r2r1_dashboard_payload_exposes_safety_activation():
    return build_s32r2r1_web_safety_payload()


def _v19898_s32r2r1_wrap(fn):
    # v19.89.8 recursion recovery:
    # automatic recursive payload wrapping disabled.
    return fn


# v19.89.8 recursion recovery: automatic global wrapping disabled
try:
    __all__
except NameError:
    __all__ = []

for _v19898_export in [
    "build_s32r2r1_web_safety_payload",
    "get_s32r2r1_web_safety_payload",
    "build_s32r2r1_dashboard_payload_exposes_safety_activation",
]:
    if _v19898_export not in __all__:
        __all__.append(_v19898_export)
# --- end v19.89.8 recovery: S32R2R1 live_web_execution_enabled exact safety contract ---
