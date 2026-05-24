from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from runtime_core.api.governed_runtime_spine_s106r1 import build_runtime_spine_contract_report

ROOT = Path.cwd()

REGISTRY_CANDIDATES = [
    "runtime_core/app.py",
    "main.py",
    "runtime_core/api/dashboard_payload_bridge.py",
    "runtime_core/api/dashboard_payload.py",
    "runtime_core/api/governed_s99_s105_routes.py",
]

FORBIDDEN_PATCH_TARGETS = [
    "runtime_core/app.py",
    "main.py",
]

SAFE_ATTACHMENT_TYPES = {
    "direct_import_contract": "safe_now",
    "dashboard_payload_read_model": "safe_after_contract",
    "route_registry_include": "safe_after_stop_gate",
    "app_py_direct_patch": "blocked",
    "main_py_direct_patch": "blocked",
}

REQUIRED_NO_PATCH_MARKERS = [
    "app_patch_performed",
    "automatic_route_registration",
]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def discover_existing_registry_surfaces(root: Path | None = None) -> Dict[str, Any]:
    base = root or ROOT
    discovered: List[Dict[str, Any]] = []

    for rel in REGISTRY_CANDIDATES:
        path = base / rel
        text = _read_text(path)
        discovered.append({
            "path": rel,
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
            "has_create_app": "def create_app" in text,
            "has_include_router": "include_router" in text,
            "has_dashboard_payload": "dashboard" in text.lower() and "payload" in text.lower(),
            "has_governed_operator_routes": "governed/operator" in text or "governed_s99_s105" in text,
            "direct_patch_allowed": rel not in FORBIDDEN_PATCH_TARGETS,
        })

    return {
        "discovery_version": "S107R1",
        "status": "registry_discovery_complete",
        "registry_candidates": discovered,
        "safe_attachment_types": dict(SAFE_ATTACHMENT_TYPES),
        "direct_app_patch_blocked": True,
        "automatic_route_registration_blocked": True,
    }


def build_safe_attachment_plan(root: Path | None = None) -> Dict[str, Any]:
    discovery = discover_existing_registry_surfaces(root)
    contract = build_runtime_spine_contract_report()

    candidates = discovery["registry_candidates"]
    dashboard_bridge = [
        item for item in candidates
        if item["exists"] and item["has_dashboard_payload"] and item["direct_patch_allowed"]
    ]
    route_registry = [
        item for item in candidates
        if item["exists"] and item["has_include_router"] and item["direct_patch_allowed"]
    ]

    plan = [
        {
            "step": 1,
            "name": "Keep S106R1 as backend module contract",
            "method": "direct_import_contract",
            "allowed_now": True,
            "patches_app": False,
        },
        {
            "step": 2,
            "name": "Attach runtime spine to dashboard payload read model only after compatibility proof",
            "method": "dashboard_payload_read_model",
            "allowed_now": bool(dashboard_bridge),
            "candidate_paths": [item["path"] for item in dashboard_bridge],
            "patches_app": False,
        },
        {
            "step": 3,
            "name": "Expose through existing governed route registry only after stop gate",
            "method": "route_registry_include",
            "allowed_now": bool(route_registry),
            "candidate_paths": [item["path"] for item in route_registry],
            "patches_app": False,
        },
        {
            "step": 4,
            "name": "Direct app.py/main.py patching",
            "method": "app_py_direct_patch",
            "allowed_now": False,
            "candidate_paths": FORBIDDEN_PATCH_TARGETS,
            "patches_app": True,
        },
    ]

    ok = (
        discovery["direct_app_patch_blocked"] is True
        and discovery["automatic_route_registration_blocked"] is True
        and contract["ok"] is True
        and all(not item["allowed_now"] for item in plan if item["method"] == "app_py_direct_patch")
    )

    return {
        "attachment_plan_version": "S107R1",
        "status": "safe_attachment_plan_ready" if ok else "safe_attachment_plan_blocked",
        "ok": ok,
        "runtime_spine_contract_ok": contract["ok"],
        "discovery": discovery,
        "plan": plan,
        "next_safe_step": "S108R1 dashboard payload read-model compatibility proof",
    }


def build_registry_discovery_report(root: Path | None = None) -> Dict[str, Any]:
    plan = build_safe_attachment_plan(root)
    return {
        "report_version": "S107R1",
        "status": "passed" if plan["ok"] else "failed",
        "ok": plan["ok"],
        "purpose": "Discover existing safe attachment surfaces without app.py patching.",
        "safe_to_continue": plan["ok"],
        "plan": plan,
    }
