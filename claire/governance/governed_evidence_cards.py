from __future__ import annotations

"""
Governed Evidence Card Normalization for Claire Syntalion.

This module converts source/search planning data into cockpit-visible evidence cards.
It intentionally performs no web execution, no provider calls, no body reads, no crawling,
no runtime mutation, no package operations, and no command execution.
"""

from datetime import datetime, timezone
from hashlib import sha1
from typing import Any

VERSION = "v19.89.8-S590-S596"

BLOCKED_CAPABILITIES: dict[str, bool] = {
    "live_web_execution_enabled": False,
    "browser_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

REVIEW_STATES: dict[str, str] = {
    "source_registered_unverified": "Registered source needs operator review before use.",
    "search_plan_unexecuted": "Search plan exists but execution remains blocked.",
    "evidence_stub_unexecuted": "Evidence placeholder exists without network evidence.",
    "quarantined_by_policy": "Policy requires quarantine before promotion.",
    "pending_operator_review": "Visible in cockpit for operator review only.",
}

EVIDENCE_POLICY: dict[str, Any] = {
    "normalization_allowed": True,
    "cockpit_render_allowed": True,
    "operator_review_allowed": True,
    "export_packet_planning_allowed": True,
    "provider_probe_allowed": False,
    "network_request_allowed": False,
    "body_read_allowed": False,
    "promotion_to_runtime_truth_allowed": False,
    "runtime_mutation_allowed": False,
    "automatic_update_allowed": False,
    "command_execution_allowed": False,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stable_id(*parts: object) -> str:
    joined = "|".join(str(part) for part in parts)
    return sha1(joined.encode("utf-8")).hexdigest()[:16]


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def get_source_registry_snapshot() -> dict[str, Any]:
    try:
        from claire.governance.governed_source_registry import get_source_registry_payload

        payload = get_source_registry_payload()
        return {
            "available": True,
            "payload": payload,
            "source_cards": _as_list(payload.get("source_cards")),
            "summary": _as_dict(payload.get("summary")),
            "readiness": payload.get("readiness", "source_registry_available"),
        }
    except Exception as exc:
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
            "payload": {},
            "source_cards": [],
            "summary": {},
            "readiness": "source_registry_not_available_fallback_active",
        }


def get_search_plan_snapshot() -> dict[str, Any]:
    try:
        from claire.governance.governed_search_plan import get_governed_search_plan_payload

        payload = get_governed_search_plan_payload()
        return {
            "available": True,
            "payload": payload,
            "search_plan_cards": _as_list(payload.get("search_plan_cards")),
            "evidence_cards": _as_list(payload.get("evidence_cards")),
            "summary": _as_dict(payload.get("summary")),
            "readiness": payload.get("readiness", "search_plan_available"),
        }
    except Exception as exc:
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
            "payload": {},
            "search_plan_cards": [],
            "evidence_cards": [],
            "summary": {},
            "readiness": "search_plan_not_available_fallback_active",
        }


def _source_title(card: dict[str, Any], index: int) -> str:
    for key in ("title", "name", "source_name", "domain", "label"):
        value = card.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    source = _as_dict(card.get("source"))
    for key in ("name", "domain", "label"):
        value = source.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"Governed source candidate {index + 1}"


def _source_tier(card: dict[str, Any]) -> str:
    for key in ("trust_tier", "tier", "source_tier"):
        value = card.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    trust = _as_dict(card.get("trust"))
    for key in ("tier", "trust_tier"):
        value = trust.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "tier_unknown_review_required"


def _source_status(card: dict[str, Any]) -> str:
    for key in ("status", "policy_status", "registry_status", "state"):
        value = card.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    policy = _as_dict(card.get("policy"))
    for key in ("status", "source_status"):
        value = policy.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "registered_pending_review"


def _source_summary(card: dict[str, Any]) -> str:
    for key in ("summary", "description", "evidence_summary"):
        value = card.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Source registry evidence is normalized for cockpit review only. No request was performed."


def normalize_source_card(card: dict[str, Any], index: int) -> dict[str, Any]:
    title = _source_title(card, index)
    tier = _source_tier(card)
    status = _source_status(card)
    review_state = "quarantined_by_policy" if "quarantine" in status.lower() else "source_registered_unverified"
    return {
        "id": f"src-{stable_id(title, tier, status, index)}",
        "version": VERSION,
        "card_type": "source_registry_evidence",
        "title": title,
        "headline": title,
        "summary": _source_summary(card),
        "source_family": card.get("source_family") or card.get("family") or "governed_source_registry",
        "trust_tier": tier,
        "source_status": status,
        "review_state": review_state,
        "review_label": REVIEW_STATES.get(review_state, review_state),
        "provenance": {
            "derived_from": "governed_source_registry",
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
            "original_card_index": index,
        },
        "policy": dict(EVIDENCE_POLICY),
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "recommended_operator_actions": [
            "review_source_tier",
            "confirm_allowlist_or_quarantine_status",
            "keep_runtime_truth_unchanged",
        ],
        "raw_reference": card,
    }


def normalize_search_plan_card(card: dict[str, Any], index: int) -> dict[str, Any]:
    title = card.get("title") or card.get("query") or card.get("intent") or f"Governed search plan {index + 1}"
    intent = card.get("intent") or _as_dict(card.get("plan")).get("intent") or "governed_search_plan"
    risk_flags = _as_list(card.get("risk_flags")) or _as_list(_as_dict(card.get("plan")).get("risk_flags"))
    review_state = "pending_operator_review" if risk_flags else "search_plan_unexecuted"
    return {
        "id": f"plan-{stable_id(title, intent, index)}",
        "version": VERSION,
        "card_type": "search_plan_evidence",
        "title": str(title),
        "headline": str(title),
        "summary": card.get("summary") or card.get("description") or "Search plan evidence is visible but unexecuted.",
        "intent": intent,
        "trust_tier": card.get("trust_tier") or "planned_tier_review_required",
        "source_status": "planned_not_executed",
        "review_state": review_state,
        "review_label": REVIEW_STATES.get(review_state, review_state),
        "risk_flags": risk_flags,
        "provenance": {
            "derived_from": "governed_search_plan",
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
            "original_card_index": index,
        },
        "policy": dict(EVIDENCE_POLICY),
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "recommended_operator_actions": [
            "review_search_intent",
            "review_source_scope",
            "leave_execution_blocked",
        ],
        "raw_reference": card,
    }


def normalize_stub_evidence_card(card: dict[str, Any], index: int) -> dict[str, Any]:
    title = card.get("title") or card.get("headline") or f"Evidence placeholder {index + 1}"
    return {
        "id": f"stub-{stable_id(title, index)}",
        "version": VERSION,
        "card_type": "evidence_stub",
        "title": str(title),
        "headline": str(card.get("headline") or title),
        "summary": card.get("summary") or "Evidence card placeholder prepared before network execution is allowed.",
        "intent": card.get("intent") or "evidence_stub",
        "trust_tier": card.get("trust_tier") or "not_assigned_no_request_performed",
        "source_status": "stub_not_executed",
        "review_state": "evidence_stub_unexecuted",
        "review_label": REVIEW_STATES["evidence_stub_unexecuted"],
        "provenance": {
            "derived_from": "governed_search_plan_evidence_stub",
            "network_request_performed": False,
            "body_read_performed": False,
            "runtime_truth_mutated": False,
            "original_card_index": index,
        },
        "policy": dict(EVIDENCE_POLICY),
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "recommended_operator_actions": [
            "review_placeholder",
            "wait_for_authorized_metadata_gate",
            "keep_runtime_truth_unchanged",
        ],
        "raw_reference": card,
    }


def build_evidence_cards() -> list[dict[str, Any]]:
    source_snapshot = get_source_registry_snapshot()
    search_snapshot = get_search_plan_snapshot()
    cards: list[dict[str, Any]] = []

    for index, card in enumerate(source_snapshot["source_cards"]):
        if isinstance(card, dict):
            cards.append(normalize_source_card(card, index))

    for index, card in enumerate(search_snapshot["search_plan_cards"]):
        if isinstance(card, dict):
            cards.append(normalize_search_plan_card(card, index))

    for index, card in enumerate(search_snapshot["evidence_cards"]):
        if isinstance(card, dict):
            cards.append(normalize_stub_evidence_card(card, index))

    if not cards:
        cards.append(
            normalize_stub_evidence_card(
                {
                    "title": "Governed evidence surface standby",
                    "headline": "Evidence cards ready; upstream source/search cards not yet available",
                    "summary": "This fallback card proves the cockpit surface without performing any network action.",
                    "intent": "fallback_surface_proof",
                },
                0,
            )
        )

    seen: set[str] = set()
    unique_cards: list[dict[str, Any]] = []
    for card in cards:
        if card["id"] in seen:
            continue
        seen.add(card["id"])
        unique_cards.append(card)
    return unique_cards


def build_review_queue(cards: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    cards = cards if cards is not None else build_evidence_cards()
    queue: list[dict[str, Any]] = []
    for priority, card in enumerate(cards, start=1):
        queue.append(
            {
                "queue_id": f"review-{card['id']}",
                "evidence_card_id": card["id"],
                "title": card["title"],
                "card_type": card["card_type"],
                "review_state": card["review_state"],
                "priority": priority,
                "operator_visible": True,
                "execution_allowed": False,
                "promotion_allowed": False,
                "network_request_performed": False,
                "body_read_performed": False,
                "runtime_truth_mutated": False,
                "required_review": card.get("recommended_operator_actions", []),
            }
        )
    return queue


def build_governed_actions(cards: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    cards = cards if cards is not None else build_evidence_cards()
    card_count = len(cards)
    return [
        {
            "id": "review_evidence_cards",
            "label": "Review evidence cards",
            "description": f"Open {card_count} normalized evidence cards for operator review.",
            "target_panel": "Evidence & Review",
            "operator_visible": True,
            "enabled": False,
            "execution_blocked": True,
            "network_request_performed": False,
            "body_read_performed": False,
            "reason": "Visual/action descriptor only; execution authority remains blocked.",
        },
        {
            "id": "quarantine_evidence_candidate",
            "label": "Mark candidate quarantine review",
            "description": "Prepare quarantine review state for suspicious source/search evidence without mutating runtime truth.",
            "target_panel": "Actions",
            "operator_visible": True,
            "enabled": False,
            "execution_blocked": True,
            "network_request_performed": False,
            "body_read_performed": False,
            "reason": "Quarantine action is visible but not executable in this phase.",
        },
        {
            "id": "prepare_evidence_export_packet",
            "label": "Prepare evidence export packet",
            "description": "Show export packet planning for reviewed evidence. No file export is performed by this action descriptor.",
            "target_panel": "Actions",
            "operator_visible": True,
            "enabled": False,
            "execution_blocked": True,
            "network_request_performed": False,
            "body_read_performed": False,
            "reason": "Export is only planned; operator-approved export remains a separate governed gate.",
        },
        {
            "id": "request_metadata_probe_gate",
            "label": "Request metadata probe gate",
            "description": "Display the next governed gate needed before any metadata-only source check could occur.",
            "target_panel": "Governed Web",
            "operator_visible": True,
            "enabled": False,
            "execution_blocked": True,
            "network_request_performed": False,
            "body_read_performed": False,
            "reason": "Metadata probes are not enabled by S590-S596.",
        },
    ]


def summarize_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    by_review_state: dict[str, int] = {}
    for card in cards:
        by_type[card["card_type"]] = by_type.get(card["card_type"], 0) + 1
        by_review_state[card["review_state"]] = by_review_state.get(card["review_state"], 0) + 1
    return {
        "total_evidence_cards": len(cards),
        "by_type": by_type,
        "by_review_state": by_review_state,
        "network_requests_performed": 0,
        "body_reads_performed": 0,
        "runtime_truth_mutations": 0,
        "operator_review_items": len(cards),
    }


def get_governed_evidence_payload() -> dict[str, Any]:
    cards = build_evidence_cards()
    review_queue = build_review_queue(cards)
    actions = build_governed_actions(cards)
    source_snapshot = get_source_registry_snapshot()
    search_snapshot = get_search_plan_snapshot()
    summary = summarize_cards(cards)
    return {
        "version": VERSION,
        "generated_at": now_iso(),
        "readiness": "governed_evidence_cards_ready_execution_blocked",
        "summary": summary,
        "policy": dict(EVIDENCE_POLICY),
        "blocked_capabilities": dict(BLOCKED_CAPABILITIES),
        "upstream_surfaces": {
            "source_registry": {
                "available": source_snapshot["available"],
                "readiness": source_snapshot.get("readiness"),
                "source_cards": len(source_snapshot.get("source_cards", [])),
            },
            "governed_search_plan": {
                "available": search_snapshot["available"],
                "readiness": search_snapshot.get("readiness"),
                "search_plan_cards": len(search_snapshot.get("search_plan_cards", [])),
                "evidence_stubs": len(search_snapshot.get("evidence_cards", [])),
            },
        },
        "evidence_cards": cards,
        "review_queue": review_queue,
        "governed_actions": actions,
        "cockpit_panels": {
            "governed_web": {
                "title": "Governed Web Evidence Surface",
                "status": "source_and_search_evidence_visible_execution_blocked",
                "cards": cards[:6],
                "actions": [action for action in actions if action["target_panel"] == "Governed Web"],
            },
            "evidence_review": {
                "title": "Evidence & Review Cards",
                "status": "normalized_cards_ready_for_operator_review",
                "cards": cards,
                "review_queue": review_queue,
            },
            "actions": {
                "title": "Governed Evidence Actions",
                "status": "actions_visible_but_not_executable",
                "actions": actions,
            },
        },
        "stop_gate": {
            "build": "S596",
            "status": "complete_when_targeted_and_full_pytest_pass",
            "next_phase": "S597-S603 Source Review Queue + Metadata Probe Gate Planning",
        },
    }


__all__ = [
    "BLOCKED_CAPABILITIES",
    "EVIDENCE_POLICY",
    "VERSION",
    "build_evidence_cards",
    "build_governed_actions",
    "build_review_queue",
    "get_governed_evidence_payload",
    "get_search_plan_snapshot",
    "get_source_registry_snapshot",
]

