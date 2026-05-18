from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Query

from claire.governance.governed_manual_metadata_probe_gate import build_manual_metadata_probe_actions, build_manual_metadata_probe_cards, build_manual_metadata_probe_payload, build_manual_metadata_probe_preflight, build_manual_metadata_probe_preview, build_manual_metadata_probe_status, build_s708_stop_gate
from claire.governance.governed_metadata_adapter_boundary import build_metadata_adapter_actions, build_metadata_adapter_boundary, build_metadata_adapter_cards, build_metadata_adapter_payload, build_metadata_adapter_status, normalize_metadata_preview, validate_metadata_result
from claire.governance.governed_provider_config_inspector import build_provider_configuration_actions, build_provider_configuration_cards, build_provider_configuration_payload, build_provider_configuration_status, inspect_provider_configurations
from claire.governance.governed_web_readiness_audit import build_activation_preflight, build_readiness_actions, build_readiness_audit, build_readiness_cards, build_readiness_payload

router = APIRouter(tags=["Governed Metadata Activation Preflight"])

@router.get("/api/search/readiness/audit")
def get_search_readiness_audit() -> dict[str, Any]:
    return build_readiness_audit()

@router.get("/api/search/readiness/preflight")
def get_search_readiness_preflight() -> dict[str, Any]:
    return build_activation_preflight()

@router.get("/api/search/readiness/cards")
def get_search_readiness_cards() -> list[dict[str, Any]]:
    return build_readiness_cards()

@router.get("/api/search/readiness/actions")
def get_search_readiness_actions() -> list[dict[str, Any]]:
    return build_readiness_actions()

@router.get("/api/search/readiness/payload")
def get_search_readiness_payload() -> dict[str, Any]:
    return build_readiness_payload()

@router.get("/api/internet/search/readiness/preflight")
def get_internet_search_readiness_preflight() -> dict[str, Any]:
    return build_activation_preflight()

@router.get("/api/search/providers/configuration")
def get_provider_configuration() -> list[dict[str, Any]]:
    return inspect_provider_configurations()

@router.get("/api/search/providers/configuration/cards")
def get_provider_configuration_cards() -> list[dict[str, Any]]:
    return build_provider_configuration_cards()

@router.get("/api/search/providers/configuration/actions")
def get_provider_configuration_actions() -> list[dict[str, Any]]:
    return build_provider_configuration_actions()

@router.get("/api/search/providers/configuration/status")
def get_provider_configuration_status() -> dict[str, Any]:
    return build_provider_configuration_status()

@router.get("/api/search/providers/configuration/payload")
def get_provider_configuration_payload() -> dict[str, Any]:
    return build_provider_configuration_payload()

@router.get("/api/search/metadata/adapter/boundary")
def get_metadata_adapter_boundary() -> dict[str, Any]:
    return build_metadata_adapter_boundary()

@router.get("/api/search/metadata/adapter/preview")
def get_metadata_adapter_preview(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return normalize_metadata_preview(query)

@router.post("/api/search/metadata/adapter/validate")
def post_validate_metadata_result(result: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return validate_metadata_result(result)

@router.get("/api/search/metadata/adapter/cards")
def get_metadata_adapter_cards(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_metadata_adapter_cards(query)

@router.get("/api/search/metadata/adapter/actions")
def get_metadata_adapter_actions() -> list[dict[str, Any]]:
    return build_metadata_adapter_actions()

@router.get("/api/search/metadata/adapter/status")
def get_metadata_adapter_status() -> dict[str, Any]:
    return build_metadata_adapter_status()

@router.get("/api/search/metadata/adapter/payload")
def get_metadata_adapter_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_metadata_adapter_payload(query)

@router.get("/api/search/metadata/probe/manual/preflight")
def get_manual_metadata_probe_preflight(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_metadata_probe_preflight(query)

@router.get("/api/search/metadata/probe/manual/preview")
def get_manual_metadata_probe_preview(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_metadata_probe_preview(query)

@router.get("/api/search/metadata/probe/manual/cards")
def get_manual_metadata_probe_cards(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_manual_metadata_probe_cards(query)

@router.get("/api/search/metadata/probe/manual/actions")
def get_manual_metadata_probe_actions(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_manual_metadata_probe_actions(query)

@router.get("/api/search/metadata/probe/manual/status")
def get_manual_metadata_probe_status(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_metadata_probe_status(query)

@router.get("/api/search/metadata/probe/manual/payload")
def get_manual_metadata_probe_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_metadata_probe_payload(query)

@router.get("/api/search/metadata/probe/manual/stop-gate")
def get_manual_metadata_probe_stop_gate() -> dict[str, Any]:
    return build_s708_stop_gate()

@router.get("/api/internet/metadata/probe/manual/preflight")
def get_internet_manual_metadata_probe_preflight(query: str | None = Query(default=None)) -> dict[str, Any]:
    return build_manual_metadata_probe_preflight(query)

@router.get("/api/cockpit/metadata-search/payload")
def get_cockpit_metadata_search_payload(query: str | None = Query(default=None)) -> dict[str, Any]:
    return {"payload_id": "s681_s708_cockpit_metadata_search_payload", "readiness": build_readiness_payload(), "provider_configuration": build_provider_configuration_payload(), "adapter_boundary": build_metadata_adapter_payload(query), "manual_probe": build_manual_metadata_probe_payload(query), "stop_gate": build_s708_stop_gate()}

@router.get("/api/cockpit/metadata-search/cards")
def get_cockpit_metadata_search_cards(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_readiness_cards() + build_provider_configuration_cards() + build_metadata_adapter_cards(query) + build_manual_metadata_probe_cards(query)

@router.get("/api/cockpit/metadata-search/actions")
def get_cockpit_metadata_search_actions(query: str | None = Query(default=None)) -> list[dict[str, Any]]:
    return build_readiness_actions() + build_provider_configuration_actions() + build_metadata_adapter_actions() + build_manual_metadata_probe_actions(query)

@router.get("/api/cockpit/metadata-search/status")
def get_cockpit_metadata_search_status(query: str | None = Query(default=None)) -> dict[str, Any]:
    return {"status": "metadata_activation_preflight_ready_execution_blocked", "stage_range": "S681-S708", "readiness": build_readiness_audit()["status"], "provider_configuration": build_provider_configuration_status(), "adapter_boundary": build_metadata_adapter_status(), "manual_probe": build_manual_metadata_probe_status(query), "network_request_performed": False, "provider_execution_allowed": False, "body_read_allowed": False}
