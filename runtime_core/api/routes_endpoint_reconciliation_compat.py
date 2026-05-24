from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from runtime_core.api.governed_metadata_activation_routes import get_search_readiness_preflight
from runtime_core.api.governed_metadata_result_routes import search_metadata_payload
from runtime_core.api.governed_provider_readiness_routes import get_provider_status
from runtime_core.api.governed_search_result_review_routes import get_cockpit_search_results_payload
from runtime_core.api.governed_source_gap_routes import get_source_gap_payload
from runtime_core.api.operator_cockpit_runtime import runtime_status_payload
from runtime_core.api.routes_governed_live_probe import post_operator_search_web_run_governed_probe
from runtime_core.governance.governed_evidence_cards import get_governed_evidence_payload
from runtime_core.governance.governed_search_plan import (
    get_governed_search_actions_payload,
    get_governed_search_plan_payload,
)


router = APIRouter(tags=["Endpoint Reconciliation Compatibility"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _alias_payload(alias_path: str, canonical_path: str, payload: Any) -> dict[str, Any]:
    return {
        "schema_version": "claire.endpoint_reconciliation.alias.v1",
        "status": "alias_resolved",
        "generated_at": _now(),
        "alias_path": alias_path,
        "canonical_path": canonical_path,
        "compatibility_only": True,
        "computed_new_truth": False,
        "payload": payload,
    }


async def _json_body(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    return body if isinstance(body, dict) else {}


@router.get("/system/runtime-state/summary")
def runtime_state_summary_alias() -> dict[str, Any]:
    return _alias_payload("/system/runtime-state/summary", "/runtime/state", runtime_status_payload())


@router.get("/system/runtime-execution/summary")
def runtime_execution_summary_alias() -> dict[str, Any]:
    return _alias_payload("/system/runtime-execution/summary", "/runtime/status", runtime_status_payload())


@router.get("/system/runtime-propagation/summary")
def runtime_propagation_summary_alias() -> dict[str, Any]:
    payload = runtime_status_payload()
    return _alias_payload(
        "/system/runtime-propagation/summary",
        "/runtime/continuous/status",
        {
            "runtime": payload,
            "propagation_status": "canonical_runtime_status_forwarded",
            "runtime_mutation_enabled": False,
        },
    )


@router.get("/api/dashboard/search/provider/status")
def dashboard_search_provider_status_alias() -> dict[str, Any]:
    return _alias_payload("/api/dashboard/search/provider/status", "/api/search/providers/status", get_provider_status())


@router.get("/api/evidence/governed/status")
def evidence_governed_status_alias() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    status_payload = {
        "version": payload.get("version"),
        "generated_at": payload.get("generated_at"),
        "readiness": payload.get("readiness"),
        "summary": payload.get("summary"),
        "upstream_surfaces": payload.get("upstream_surfaces"),
        "stop_gate": payload.get("stop_gate"),
        "blocked_capabilities": payload.get("blocked_capabilities"),
    }
    return _alias_payload("/api/evidence/governed/status", "/api/evidence/quarantine/status", status_payload)


@router.get("/api/evidence/governed/cards")
def evidence_governed_cards_alias() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return _alias_payload(
        "/api/evidence/governed/cards",
        "/api/evidence/quarantine/cards",
        {"evidence_cards": payload.get("evidence_cards", []), "summary": payload.get("summary", {})},
    )


@router.get("/api/evidence/governed/actions")
def evidence_governed_actions_alias() -> dict[str, Any]:
    payload = get_governed_evidence_payload()
    return _alias_payload(
        "/api/evidence/governed/actions",
        "/api/evidence/quarantine/actions",
        {"governed_actions": payload.get("governed_actions", []), "blocked_capabilities": payload.get("blocked_capabilities", {})},
    )


@router.get("/api/search/governed/plans")
def search_governed_plans_alias() -> dict[str, Any]:
    return _alias_payload("/api/search/governed/plans", "/api/search/governed/query/payload", get_governed_search_plan_payload())


@router.get("/api/search/governed/actions")
def search_governed_actions_alias() -> dict[str, Any]:
    return _alias_payload("/api/search/governed/actions", "/api/search/governed/query/actions", get_governed_search_actions_payload())


@router.get("/api/search/readiness/preflight")
def search_readiness_preflight_alias() -> dict[str, Any]:
    return _alias_payload("/api/search/readiness/preflight", "/api/search/readiness/audit", get_search_readiness_preflight())


@router.get("/api/search/metadata/payload")
def search_metadata_payload_alias() -> dict[str, Any]:
    return _alias_payload("/api/search/metadata/payload", "/api/search/metadata/adapter/payload", search_metadata_payload())


@router.get("/api/cockpit/search-results/payload")
def cockpit_search_results_payload_alias() -> dict[str, Any]:
    return _alias_payload("/api/cockpit/search-results/payload", "/api/evidence/quarantine/payload", get_cockpit_search_results_payload())


@router.get("/api/sources/gaps/payload")
def sources_gaps_payload_alias() -> dict[str, Any]:
    return _alias_payload("/api/sources/gaps/payload", "/api/sources/policy/payload", get_source_gap_payload())


@router.post("/api/internet/live-toggle/preflight")
async def internet_live_toggle_preflight_alias(request: Request) -> JSONResponse:
    body = await _json_body(request)
    return JSONResponse(
        _alias_payload(
            "/api/internet/live-toggle/preflight",
            "/internet/live-probe/status",
            {
                "status": "preflight_review_only",
                "operator_confirmed": bool(body.get("operator_confirmed")),
                "live_execution_enabled": False,
                "dashboard_can_enable": False,
            },
        )
    )


@router.post("/api/internet/provider/probe")
async def internet_provider_probe_alias(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    payload = post_operator_search_web_run_governed_probe(
        {
            "query": body.get("query") or body.get("source_url") or "provider probe compatibility alias",
            "confirm_text": body.get("confirm_text") or "CONFIRM",
            "operator_confirmed": body.get("operator_confirmed", False),
            "allow_live_execution": body.get("allow_live_execution", False),
        }
    )
    return _alias_payload("/api/internet/provider/probe", "/operator/search/web/run-governed-probe", payload)


@router.post("/api/internet/fetch/controlled")
async def internet_fetch_controlled_alias(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    return _alias_payload(
        "/api/internet/fetch/controlled",
        "/internet/live-probe/run",
        {
            "status": "controlled_fetch_alias_review_only",
            "source_url": body.get("source_url"),
            "network_request_performed": False,
            "body_read_performed": False,
            "quarantine_required": True,
        },
    )


@router.get("/api/internet/fetch/controlled/status")
def internet_fetch_controlled_status_alias() -> dict[str, Any]:
    return _alias_payload(
        "/api/internet/fetch/controlled/status",
        "/internet/live-probe/status",
        {"status": "controlled_fetch_alias_ready", "network_request_performed": False},
    )


@router.post("/api/internet/live-metadata/run")
async def internet_live_metadata_run_alias(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    return _alias_payload(
        "/api/internet/live-metadata/run",
        "/internet/live-probe/run",
        {
            "status": "metadata_run_alias_review_only",
            "source_url": body.get("source_url"),
            "allow_live_execution": bool(body.get("allow_live_execution")),
            "network_request_performed": False,
            "body_read_performed": False,
        },
    )


@router.get("/api/internet/live-metadata/run/status")
def internet_live_metadata_run_status_alias() -> dict[str, Any]:
    return _alias_payload(
        "/api/internet/live-metadata/run/status",
        "/internet/live-probe/status",
        {"status": "metadata_run_alias_ready", "network_request_performed": False},
    )


@router.post("/api/internet/proposals/review")
async def internet_proposals_review_alias(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    return _alias_payload(
        "/api/internet/proposals/review",
        "/api/update-governance/open-web/request",
        {
            "status": "review_recorded_compatibility_only",
            "action": body.get("action") or "review",
            "operator_confirmed": bool(body.get("operator_confirmed")),
            "runtime_truth_modified": False,
            "install_performed": False,
        },
    )


@router.post("/api/internet/proposals/export")
async def internet_proposals_export_alias(request: Request) -> dict[str, Any]:
    body = await _json_body(request)
    return _alias_payload(
        "/api/internet/proposals/export",
        "/api/update-governance/open-web/panel",
        {
            "status": "export_preview_compatibility_only",
            "operator_confirmed": bool(body.get("operator_confirmed")),
            "export_package_written": False,
            "install_performed": False,
        },
    )


@router.get("/api/internet/proposals/status")
def internet_proposals_status_alias() -> dict[str, Any]:
    return _alias_payload(
        "/api/internet/proposals/status",
        "/api/update-governance/open-web/panel",
        {"status": "proposal_alias_ready", "install_performed": False},
    )

