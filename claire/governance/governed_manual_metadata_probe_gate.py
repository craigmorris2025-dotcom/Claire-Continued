from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

from claire.governance.governed_metadata_adapter_boundary import normalize_metadata_preview
from claire.governance.governed_provider_config_inspector import inspect_provider_configurations
from claire.governance.governed_web_readiness_audit import build_activation_preflight

BLOCKED_AUTHORITY: dict[str, bool] = {
    "live_web_execution_enabled": False,
    "search_provider_execution_enabled": False,
    "browser_execution_enabled": False,
    "network_request_performed": False,
    "body_read_allowed": False,
    "autonomous_crawling_enabled": False,
    "automatic_updates_enabled": False,
    "runtime_mutation_enabled": False,
    "package_download_performed": False,
    "package_install_performed": False,
    "command_execution_enabled": False,
}

@dataclass(frozen=True)
class ManualMetadataProbeGate:
    gate_id: str
    stage_range: str
    query: str
    status: str
    execution_allowed: bool
    provider_execution_allowed: bool
    network_request_performed: bool
    body_read_allowed: bool
    preview_results_available: bool
    real_results_available: bool
    result_path: str
    blocked_authority: dict[str, bool]


def _gate_id(query: str) -> str:
    return "manual_metadata_probe_" + sha256(query.strip().lower().encode("utf-8")).hexdigest()[:12]


def build_manual_metadata_probe_preflight(query: str | None = None) -> dict[str, Any]:
    clean_query = (query or "Claire governed metadata search readiness").strip()
    return asdict(ManualMetadataProbeGate(gate_id=_gate_id(clean_query), stage_range="S702-S708", query=clean_query, status="manual_metadata_probe_gate_ready_execution_blocked", execution_allowed=False, provider_execution_allowed=False, network_request_performed=False, body_read_allowed=False, preview_results_available=True, real_results_available=False, result_path="provider_metadata -> quarantine_store -> evidence_card -> operator_review -> evidence_basket_preview", blocked_authority=BLOCKED_AUTHORITY.copy()))


def build_manual_metadata_probe_preview(query: str | None = None) -> dict[str, Any]:
    clean_query = (query or "Claire governed metadata search readiness").strip()
    return {"preview_id": _gate_id(clean_query) + "_preview", "status": "local_preview_only_no_network", "query": clean_query, "network_request_performed": False, "provider_execution_allowed": False, "body_read_allowed": False, "preview_results": normalize_metadata_preview(clean_query), "note": "These are local contract-preview records, not live web results."}


def build_manual_metadata_probe_cards(query: str | None = None) -> list[dict[str, Any]]:
    preflight = build_manual_metadata_probe_preflight(query)
    preview = build_manual_metadata_probe_preview(preflight["query"])
    configured = inspect_provider_configurations()
    return [
        {"card_id": "manual_metadata_probe_gate", "title": "Manual metadata search probe gate", "status": "ready_blocked", "summary": "The command/search path can prepare a metadata probe, but cannot execute a provider request yet.", "query": preflight["query"], "result_path": preflight["result_path"], "blocked_authority": BLOCKED_AUTHORITY.copy()},
        {"card_id": "provider_execution_configuration", "title": "Provider execution configuration", "status": "inspected_execution_blocked", "summary": "Provider config can be inspected without secrets and without network calls.", "providers": configured},
        {"card_id": "metadata_probe_preview_results", "title": "Probe preview result shape", "status": "preview_only_no_network", "summary": "Local preview records show what the cockpit can render after a later live metadata unlock.", "results": preview["preview_results"]},
    ]


def build_manual_metadata_probe_actions(query: str | None = None) -> list[dict[str, Any]]:
    preflight = build_manual_metadata_probe_preflight(query)
    return [
        {"action_id": "review_manual_metadata_probe_preflight", "label": "Review manual metadata probe preflight", "status": "available_for_review", "executable": False, "endpoint": "/api/search/metadata/probe/manual/preflight", "gate_id": preflight["gate_id"]},
        {"action_id": "preview_metadata_result_contract", "label": "Preview metadata result contract", "status": "available_for_review", "executable": False, "endpoint": "/api/search/metadata/probe/manual/preview", "reason": "Local preview only; no network request."},
        {"action_id": "execute_manual_metadata_probe", "label": "Execute manual metadata probe", "status": "blocked", "executable": False, "endpoint": None, "reason": "Real provider/network execution is not enabled in S681-S708."},
    ]


def build_manual_metadata_probe_status(query: str | None = None) -> dict[str, Any]:
    preflight = build_manual_metadata_probe_preflight(query)
    return {"status": "manual_metadata_probe_gate_ready_execution_blocked", "stage_range": "S702-S708", "query": preflight["query"], "manual_gate_present": True, "preview_results_available": True, "real_results_available": False, "provider_execution_allowed": False, "network_request_performed": False, "body_read_allowed": False, "next_phase": "S709-S736 result quarantine, evidence normalization, confidence and review actions", "blocked_authority": BLOCKED_AUTHORITY.copy()}


def build_manual_metadata_probe_payload(query: str | None = None) -> dict[str, Any]:
    return {"payload_id": "s702_s708_manual_metadata_probe_gate_payload", "activation_preflight": build_activation_preflight(), "preflight": build_manual_metadata_probe_preflight(query), "preview": build_manual_metadata_probe_preview(query), "cards": build_manual_metadata_probe_cards(query), "actions": build_manual_metadata_probe_actions(query), "status": build_manual_metadata_probe_status(query)}


def build_s708_stop_gate() -> dict[str, Any]:
    return {"stop_gate_id": "s708_manual_metadata_probe_gate", "status": "complete_execution_still_blocked", "completed_ranges": ["S681-S687", "S688-S694", "S695-S701", "S702-S708"], "proof": ["search/web readiness audit exists", "provider configuration inspector exists", "metadata-only adapter boundary exists", "manual metadata probe gate exists", "local preview records can render without network execution"], "current_state": {"live_web_execution_enabled": False, "search_provider_execution_enabled": False, "network_request_performed": False, "body_read_allowed": False, "runtime_mutation_enabled": False, "automatic_updates_enabled": False, "next_phase": "S709-S736 result quarantine and cockpit evidence/result visibility"}}
