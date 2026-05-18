from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from claire.governance.governed_cockpit_search_consolidation import (
    build_cockpit_search_actions,
    build_cockpit_search_cards,
    build_cockpit_search_status,
    build_cockpit_search_stop_gate,
    build_cockpit_source_search_consolidation,
)
from claire.governance.governed_evidence_lifecycle_preview import (
    build_evidence_lifecycle_routing_preview,
    build_lifecycle_preview_actions,
    build_lifecycle_preview_cards,
    build_lifecycle_preview_payload,
    build_lifecycle_preview_status,
)
from claire.governance.governed_manual_provider_probe import (
    build_manual_probe_actions,
    build_manual_probe_cards,
    build_manual_probe_payload,
    build_manual_probe_policy,
    build_manual_probe_preflight,
    build_manual_probe_status,
)
from claire.governance.governed_search_evidence_bridge import (
    build_search_evidence_actions,
    build_search_evidence_cards,
    build_search_evidence_payload,
    build_search_evidence_status,
    build_search_to_evidence_bridge,
)

router = APIRouter(tags=["Governed Controlled Metadata Search"])


@router.get("/api/search/provider/manual-probe/preflight")
def manual_probe_preflight(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_probe_preflight(query)


@router.get("/api/search/provider/manual-probe/cards")
def manual_probe_cards(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_manual_probe_cards(query)


@router.get("/api/search/provider/manual-probe/actions")
def manual_probe_actions(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_manual_probe_actions(query)


@router.get("/api/search/provider/manual-probe/policy")
def manual_probe_policy() -> dict[str, Any]:
    return build_manual_probe_policy()


@router.get("/api/search/provider/manual-probe/status")
def manual_probe_status() -> dict[str, Any]:
    return build_manual_probe_status()


@router.get("/api/search/provider/manual-probe/payload")
def manual_probe_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_probe_payload(query)


@router.get("/api/search/provider/manual-probe/stop-gate")
def manual_probe_stop_gate() -> dict[str, Any]:
    status = build_manual_probe_status()
    return {
        "stop_gate_id": "s659_manual_metadata_provider_probe_gate",
        "status": status["status"],
        "passed": status["manual_probe_gate_present"] and not status["network_request_performed"],
        "network_request_performed": False,
        "body_read_allowed": False,
    }


@router.get("/api/internet/provider/manual-probe/preflight")
def internet_manual_probe_preflight(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_probe_preflight(query)


@router.get("/api/search/evidence/bridge/preview")
def search_evidence_bridge_preview() -> dict[str, Any]:
    return build_search_to_evidence_bridge()


@router.get("/api/search/evidence/bridge/cards")
def search_evidence_bridge_cards() -> list[dict[str, Any]]:
    return build_search_evidence_cards()


@router.get("/api/search/evidence/bridge/actions")
def search_evidence_bridge_actions() -> list[dict[str, Any]]:
    return build_search_evidence_actions()


@router.get("/api/search/evidence/bridge/status")
def search_evidence_bridge_status() -> dict[str, Any]:
    return build_search_evidence_status()


@router.get("/api/search/evidence/bridge/payload")
def search_evidence_bridge_payload() -> dict[str, Any]:
    return build_search_evidence_payload()


@router.get("/api/search/evidence/bridge/stop-gate")
def search_evidence_bridge_stop_gate() -> dict[str, Any]:
    status = build_search_evidence_status()
    return {
        "stop_gate_id": "s666_search_to_evidence_bridge",
        "passed": status["metadata_to_evidence_bridge_present"] and status["quarantine_first"],
        "runtime_truth_mutated": False,
        "network_request_performed": False,
    }


@router.get("/api/evidence/lifecycle/routing-preview")
def evidence_lifecycle_routing_preview() -> dict[str, Any]:
    return build_evidence_lifecycle_routing_preview()


@router.get("/api/evidence/lifecycle/cards")
def evidence_lifecycle_cards() -> list[dict[str, Any]]:
    return build_lifecycle_preview_cards()


@router.get("/api/evidence/lifecycle/actions")
def evidence_lifecycle_actions() -> list[dict[str, Any]]:
    return build_lifecycle_preview_actions()


@router.get("/api/evidence/lifecycle/status")
def evidence_lifecycle_status() -> dict[str, Any]:
    return build_lifecycle_preview_status()


@router.get("/api/evidence/lifecycle/payload")
def evidence_lifecycle_payload() -> dict[str, Any]:
    return build_lifecycle_preview_payload()


@router.get("/api/evidence/lifecycle/stop-gate")
def evidence_lifecycle_stop_gate() -> dict[str, Any]:
    status = build_lifecycle_preview_status()
    return {
        "stop_gate_id": "s673_evidence_to_lifecycle_preview",
        "passed": status["route_previews_present"] and status["lifecycle_mutated"] is False,
        "lifecycle_mutated": False,
        "runtime_truth_mutated": False,
    }


@router.get("/api/cockpit/search/consolidated-payload")
def cockpit_search_consolidated_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_cockpit_source_search_consolidation(query)


@router.get("/api/cockpit/search/cards")
def cockpit_search_cards(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_cockpit_search_cards(query)


@router.get("/api/cockpit/search/actions")
def cockpit_search_actions(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_cockpit_search_actions(query)


@router.get("/api/cockpit/search/status")
def cockpit_search_status() -> dict[str, Any]:
    return build_cockpit_search_status()


@router.get("/api/cockpit/search/stop-gate")
def cockpit_search_stop_gate() -> dict[str, Any]:
    return build_cockpit_search_stop_gate()


@router.get("/api/internet/search/consolidated-payload")
def internet_search_consolidated_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_cockpit_source_search_consolidation(query)
