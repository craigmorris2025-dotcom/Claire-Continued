from __future__ import annotations

from typing import Any

from runtime_core.governance.governed_evidence_lifecycle_preview import (
    build_lifecycle_preview_actions,
    build_lifecycle_preview_cards,
    build_lifecycle_preview_payload,
)
from runtime_core.governance.governed_manual_provider_probe import (
    BLOCKED_AUTHORITY,
    build_manual_probe_actions,
    build_manual_probe_cards,
    build_manual_probe_payload,
)
from runtime_core.governance.governed_search_evidence_bridge import (
    build_search_evidence_actions,
    build_search_evidence_cards,
    build_search_evidence_payload,
)


def _flatten(list_of_lists: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in list_of_lists:
        items.extend(group)
    return items


def build_cockpit_source_search_consolidation(query: str | None = None) -> dict[str, Any]:
    manual_probe = build_manual_probe_payload(query)
    bridge = build_search_evidence_payload()
    lifecycle = build_lifecycle_preview_payload()
    panels = [
        {
            "panel_id": "manual_provider_probe",
            "title": "Manual metadata provider probe",
            "status": manual_probe["status"]["status"],
            "stage_range": "S653-S659",
            "cards": manual_probe["cards"],
        },
        {
            "panel_id": "search_to_evidence_bridge",
            "title": "Search-to-evidence bridge",
            "status": bridge["status"]["status"],
            "stage_range": "S660-S666",
            "cards": bridge["cards"],
        },
        {
            "panel_id": "evidence_lifecycle_preview",
            "title": "Evidence-to-lifecycle routing preview",
            "status": lifecycle["status"]["status"],
            "stage_range": "S667-S673",
            "cards": lifecycle["cards"],
        },
        {
            "panel_id": "source_search_stop_gate",
            "title": "Cockpit source/search consolidation stop gate",
            "status": "s680_ready_blocked",
            "stage_range": "S674-S680",
            "cards": [
                {
                    "card_id": "s680_stop_gate",
                    "title": "S680 source/search cockpit consolidation",
                    "status": "ready_for_operator_review",
                    "summary": "Governed Web, Evidence & Review, Actions, and System can now present a consolidated source/search state without enabling live search.",
                    "still_blocked": [key for key, value in BLOCKED_AUTHORITY.items() if value is False],
                }
            ],
        },
    ]
    actions = _flatten([
        build_manual_probe_actions(query),
        build_search_evidence_actions(),
        build_lifecycle_preview_actions(),
        [
            {
                "action_id": "s680_review_consolidated_source_search_state",
                "label": "Review consolidated source/search state",
                "status": "available_for_review",
                "executable": False,
                "endpoint": "/api/cockpit/search/consolidated-payload",
                "reason": "Visible cockpit review only; no search execution or mutation is enabled.",
            }
        ],
    ])
    cards = _flatten([panel["cards"] for panel in panels])
    return {
        "payload_id": "s653_s680_governed_controlled_metadata_search_cockpit",
        "version": "v19.89.8",
        "stage_range": "S653-S680",
        "status": "consolidated_source_search_ready_blocked",
        "milestone": "S680 cockpit source/search consolidation stop gate",
        "query": (query or "sample governed metadata probe").strip(),
        "panels": panels,
        "cards": cards,
        "actions": actions,
        "blocked_authority": BLOCKED_AUTHORITY.copy(),
        "proof": {
            "manual_probe_gate_present": True,
            "search_to_evidence_bridge_present": True,
            "evidence_to_lifecycle_preview_present": True,
            "cockpit_consolidation_present": True,
            "live_web_execution_enabled": False,
            "network_request_performed": False,
            "body_read_allowed": False,
            "runtime_mutation_enabled": False,
        },
    }


def build_cockpit_search_cards(query: str | None = None) -> list[dict[str, Any]]:
    return build_cockpit_source_search_consolidation(query)["cards"]


def build_cockpit_search_actions(query: str | None = None) -> list[dict[str, Any]]:
    return build_cockpit_source_search_consolidation(query)["actions"]


def build_cockpit_search_status() -> dict[str, Any]:
    return {
        "status": "s680_ready_blocked",
        "stage_range": "S653-S680",
        "next_phase": "S681-S694 search/web readiness audit and provider configuration inspector",
        "live_web_execution_enabled": False,
        "search_provider_execution_enabled": False,
        "network_request_performed": False,
        "body_read_allowed": False,
        "autonomous_crawling_enabled": False,
        "runtime_mutation_enabled": False,
    }


def build_cockpit_search_stop_gate() -> dict[str, Any]:
    return {
        "stop_gate_id": "s680_cockpit_source_search_consolidation",
        "passed_when": [
            "manual probe preflight routes are visible",
            "metadata search-to-evidence bridge is visible",
            "evidence-to-lifecycle routing preview is visible",
            "consolidated cockpit payload is visible",
            "all blocked authorities remain false",
        ],
        "current_state": build_cockpit_search_status(),
    }
