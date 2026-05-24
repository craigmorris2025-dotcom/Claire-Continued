from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter


router = APIRouter(tags=["Cockpit Runtime Synchronization"])

_BACKEND_TRUTH_SURFACES: List[str] = [
    "/health",
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/runtime/continuous/status",
    "/runtime/continuous/review-queue",
    "/api/cockpit/operational-status",
    "/api/operational-proof/status",
    "/api/cockpit/operational-proof",
]

_GOVERNED_SEARCH_SURFACES: List[str] = [
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
]

_LIVE_SOURCE_SURFACES: List[str] = [
    "/api/feeds/live-source-catalog/status",
    "/api/feeds/live-source-catalog/health",
    "/api/live-intelligence/status",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _runtime_sync_contract() -> Dict[str, Any]:
    return {
        "version": "v19.88.7",
        "build": "Cockpit Runtime Synchronization Surface",
        "status": "mounted",
        "sync_state": "backend_truth_bound",
        "timestamp_utc": _utc_now(),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_over_ui_assumptions": True,
        "creates_new_truth": False,
        "runtime_truth_mutation": False,
        "uncontrolled_browsing_enabled": False,
        "autonomous_execution_enabled": False,
        "fake_ai_agent_behavior_enabled": False,
        "fail_closed_governance": True,
        "manual_enable_required_for_probe": True,
        "operator_probe_auto_enable": False,
        "backend_truth_surfaces": list(_BACKEND_TRUTH_SURFACES),
        "governed_search_surfaces": list(_GOVERNED_SEARCH_SURFACES),
        "live_source_surfaces": list(_LIVE_SOURCE_SURFACES),
        "cockpit_binding": {
            "purpose": "presentation_alias_and_status_synchronization",
            "truth_source": "backend_runtime_and_operational_proof_surfaces",
            "creates_or_overrides_backend_state": False,
            "safe_to_poll": True,
        },
    }


@router.get("/api/cockpit/runtime-sync/status")
def cockpit_runtime_sync_status() -> Dict[str, Any]:
    return _runtime_sync_contract()


@router.get("/api/cockpit/runtime-sync/heartbeat")
def cockpit_runtime_sync_heartbeat() -> Dict[str, Any]:
    payload = _runtime_sync_contract()
    payload["heartbeat"] = {
        "status": "ok",
        "source": "backend_owned_runtime_sync_contract",
        "presentation_only": True,
        "mutates_runtime": False,
    }
    return payload


@router.get("/cockpit/runtime-sync")
def cockpit_runtime_sync_page() -> Dict[str, Any]:
    payload = _runtime_sync_contract()
    payload["page"] = {
        "type": "cockpit_presentation_alias",
        "recommended_fetch": "/api/cockpit/runtime-sync/status",
        "note": "Cockpit page alias only; backend remains source of truth.",
    }
    return payload
