from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from runtime_core.lifecycle.lifecycle_registry import CoreLifecycleRegistry
from runtime_core.lifecycle.threshold_provenance import ThresholdProvenance
from runtime_core.config.env import getenv


ROOT = Path(__file__).resolve().parents[2]


REQUIRED_OPERATIONAL_ROUTES = [
    "/health",
    "/dashboard/payload",
    "/api/operational/control-plane",
    "/api/operational/route-health",
    "/api/lifecycle/stage-registry",
    "/api/lifecycle/threshold-provenance",
    "/api/source-lineage/status",
    "/api/update/status",
    "/api/platform/update/plan",
    "/api/governed/live-probe/status",
    "/runtime/continuous/status",
    "/runtime/continuous/start",
    "/runtime/continuous/review-queue",
    "/api/governed/runtime-spine",
    "/api/cockpit/command/latest",
    "/evaluate",
]


REQUIRED_OPERATIONAL_FILES = [
    "runtime_core/app.py",
    "runtime_core/dashboard/final_dashboard_payload.py",
    "runtime_core/dashboard/operational_control_plane.py",
    "runtime_core/lifecycle/lifecycle_registry.py",
    "runtime_core/lifecycle/threshold_provenance.py",
    "runtime_core/data_lineage/source_record_builder.py",
    "runtime_core/data_lineage/provenance_tracker.py",
    "runtime_core/platform/update_governance/update_orchestrator.py",
    "runtime_core/platform/update_governance/rollback_orchestrator.py",
    "runtime_core/platform/update_governance/validation_gauntlet.py",
    "frontend/operator_dashboard/v5/index.html",
    "frontend/operator_dashboard/v5/dashboard_v5.css",
    "frontend/operator_dashboard/v5/dashboard_v5.js",
]


INTERNET_ENV_KEYS = [
    "PLATFORM_SEARCH_PROVIDER",
    "BING_SEARCH_API_KEY",
    "BRAVE_SEARCH_API_KEY",
    "SERPAPI_API_KEY",
    "TAVILY_API_KEY",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def file_readiness() -> dict[str, Any]:
    files = [
        {
            "path": rel_path,
            "exists": _exists(rel_path),
            "required_for": "final_operator_dashboard",
        }
        for rel_path in REQUIRED_OPERATIONAL_FILES
    ]
    return {
        "status": "ready" if all(item["exists"] for item in files) else "missing_files",
        "required_count": len(files),
        "present_count": len([item for item in files if item["exists"]]),
        "missing": [item["path"] for item in files if not item["exists"]],
        "files": files,
    }


def route_health(routes: Iterable[Any]) -> dict[str, Any]:
    mounted = {getattr(route, "path", "") for route in routes}
    checks = [
        {
            "path": path,
            "mounted": path in mounted,
            "required_for": "final_operator_dashboard",
        }
        for path in REQUIRED_OPERATIONAL_ROUTES
    ]
    return {
        "status": "ready" if all(item["mounted"] for item in checks) else "missing_routes",
        "required_count": len(checks),
        "mounted_count": len([item for item in checks if item["mounted"]]),
        "missing": [item["path"] for item in checks if not item["mounted"]],
        "routes": checks,
    }


def internet_authority_status() -> dict[str, Any]:
    selected_provider = getenv("PLATFORM_SEARCH_PROVIDER").strip().lower() or "none"
    key_state = {
        key: {
            "present": bool(getenv(key) if key.startswith("PLATFORM_") else os.environ.get(key)),
            "redacted": "***" if (getenv(key) if key.startswith("PLATFORM_") else os.environ.get(key)) else "",
        }
        for key in INTERNET_ENV_KEYS
    }
    provider_key_present = any(key_state[key]["present"] for key in INTERNET_ENV_KEYS if key != "PLATFORM_SEARCH_PROVIDER")
    enabled = selected_provider != "none" and provider_key_present
    return {
        "status": "configured_but_locked" if enabled else "provider_not_configured",
        "live_search_enabled": False,
        "live_internet_enabled": False,
        "automatic_updates_enabled": False,
        "selected_provider": selected_provider,
        "provider_key_present": provider_key_present,
        "keys": key_state,
        "blocked_until": [
            "operator_approval",
            "source_allowlist",
            "quarantine_policy",
            "rate_limits",
            "evidence_capture",
            "rollback_policy",
        ],
    }


def source_lineage_status() -> dict[str, Any]:
    lineage_files = [
        "runtime_core/data_lineage/source_record_builder.py",
        "runtime_core/data_lineage/provenance_tracker.py",
        "runtime_core/data_lineage/citation_anchor_registry.py",
        "runtime_core/data_lineage/transformation_chain.py",
        "runtime_core/operational_evidence/lineage_record.py",
        "data/proof/evidence_binder.json",
        "data/proof/proof_records.json",
    ]
    files = [{"path": path, "exists": _exists(path)} for path in lineage_files]
    return {
        "status": "ready" if all(item["exists"] for item in files[:5]) else "partial",
        "logger_available": _exists("runtime_core/operational_evidence/lineage_record.py"),
        "provenance_tracker_available": _exists("runtime_core/data_lineage/provenance_tracker.py"),
        "evidence_binder_available": _exists("data/proof/evidence_binder.json"),
        "files": files,
        "dashboard_action": "inspect_evidence_basket",
    }


def update_status() -> dict[str, Any]:
    missing_policy_files = [
        path
        for path in [
            "claire/platform/update_governance/update_plan.py",
            "claire/platform/update_governance/rollback_policy.py",
        ]
        if not _exists(path)
    ]
    return {
        "status": "locked_missing_policy_files" if missing_policy_files else "locked_ready_for_operator_plan",
        "automatic_updates_enabled": False,
        "manual_update_review_enabled": True,
        "execution_enabled": False,
        "rollback_required": True,
        "missing_policy_files": missing_policy_files,
        "available_files": {
            "update_orchestrator": _exists("claire/platform/update_governance/update_orchestrator.py"),
            "rollback_orchestrator": _exists("claire/platform/update_governance/rollback_orchestrator.py"),
            "validation_gauntlet": _exists("claire/platform/update_governance/validation_gauntlet.py"),
            "safe_installer": _exists("safe_install_claire_version.py"),
        },
    }


def update_plan() -> dict[str, Any]:
    status = update_status()
    return {
        "record_type": "operator_update_plan",
        "status": "blocked" if status["missing_policy_files"] else "review_required",
        "execution_enabled": False,
        "automatic_execution_enabled": False,
        "operator_review_required": True,
        "rollback_required": True,
        "required_validation": ["provider_gate", "source_trust", "rollback_plan", "pytest", "launcher_test", "dashboard_test"],
        "missing_policy_files": status["missing_policy_files"],
        "next_actions": [
            "create_missing_update_policy_files",
            "bind_update_status_to_dashboard",
            "require_operator_approval_before_execution",
            "run_validation_gauntlet_before_unlock",
        ],
    }


def operational_actions() -> list[dict[str, Any]]:
    return [
        {"id": "refresh_operational_state", "category": "System", "label": "Refresh Operational State", "method": "GET", "endpoint": "/api/operational/control-plane"},
        {"id": "check_route_health", "category": "System", "label": "Check Route Health", "method": "GET", "endpoint": "/api/operational/route-health"},
        {"id": "start_continuous_runtime", "category": "Runtime", "label": "Start Governed Runtime Cycle", "method": "POST", "endpoint": "/runtime/continuous/start", "body": {"operator_approved": False, "source": "dashboard_v5"}},
        {"id": "open_review_queue", "category": "Runtime", "label": "Open Review Queue", "method": "GET", "endpoint": "/runtime/continuous/review-queue"},
        {"id": "open_runtime_spine", "category": "Runtime", "label": "Open Runtime Spine", "method": "GET", "endpoint": "/api/governed/runtime-spine"},
        {"id": "evaluate_demo_payload", "category": "Pipeline", "label": "Evaluate Demo Payload", "method": "POST", "endpoint": "/evaluate", "body": {"query": "dashboard operator smoke payload", "source": "dashboard_v5"}},
        {"id": "open_lifecycle_registry", "category": "Lifecycle", "label": "Open Lifecycle Registry", "method": "GET", "endpoint": "/api/lifecycle/stage-registry"},
        {"id": "open_thresholds", "category": "Lifecycle", "label": "Open Threshold Provenance", "method": "GET", "endpoint": "/api/lifecycle/threshold-provenance"},
        {"id": "inspect_source_lineage", "category": "Evidence", "label": "Inspect Source Lineage", "method": "GET", "endpoint": "/api/source-lineage/status"},
        {"id": "open_search_plans", "category": "Internet", "label": "Open Governed Search Plans", "method": "GET", "endpoint": "/api/cockpit/command/latest"},
        {"id": "check_internet_authority", "category": "Internet", "label": "Check Internet Authority", "method": "GET", "endpoint": "/api/governed/live-probe/status"},
        {"id": "review_update_status", "category": "Updates", "label": "Review Update Status", "method": "GET", "endpoint": "/api/update/status"},
        {"id": "review_update_plan", "category": "Updates", "label": "Review Update Plan", "method": "GET", "endpoint": "/api/platform/update/plan"},
    ]


def lifecycle_registry_payload() -> dict[str, Any]:
    return CoreLifecycleRegistry().as_payload()


def threshold_provenance_payload() -> dict[str, Any]:
    return ThresholdProvenance().as_payload()


def build_operational_control_plane(routes: Iterable[Any] = ()) -> dict[str, Any]:
    route_status = route_health(routes)
    file_status = file_readiness()
    internet_status = internet_authority_status()
    update_state = update_status()
    lineage = source_lineage_status()
    checks = {
        "required_routes_mounted": route_status["status"] == "ready",
        "required_files_present": file_status["status"] == "ready",
        "lifecycle_registry_available": True,
        "threshold_provenance_available": True,
        "source_lineage_available": lineage["status"] == "ready",
        "update_governance_safe_locked": update_state["automatic_updates_enabled"] is False,
        "internet_safe_locked": internet_status["live_internet_enabled"] is False,
    }
    completion = int((len([value for value in checks.values() if value]) / len(checks)) * 100)
    return {
        "schema_version": "claire_operational_control_plane_v1",
        "generated_at": utc_now(),
        "status": "operational_ready" if completion == 100 else "operational_partial",
        "completion_percent": completion,
        "checks": checks,
        "route_health": route_status,
        "file_readiness": file_status,
        "source_lineage": lineage,
        "internet_authority": internet_status,
        "update_governance": update_state,
        "update_plan": update_plan(),
        "actions": operational_actions(),
        "blocked_authorities": [
            "live_search_execution",
            "live_internet_execution",
            "automatic_updates",
            "runtime_mutation",
            "autonomous_external_actions",
        ],
    }
