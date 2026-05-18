from __future__ import annotations

from typing import Any

from claire.api.s44_dashboard_consumption_manifest import (
    build_dashboard_consumption_manifest,
    verify_dashboard_consumption_manifest,
)
from claire.api.s44_cockpit_surface_health_snapshot import (
    build_s44r9_r16_plateau_report,
)


S45_VERSION = "v19.89.8-S45R1-R8"
S45_BRIDGE_ASSET_ROOT = "frontend/cockpit/s45_bridge"


def build_cockpit_ui_bridge_manifest() -> dict[str, Any]:
    consumption = build_dashboard_consumption_manifest()
    plateau = build_s44r9_r16_plateau_report()

    bridge_surfaces = []
    for surface in consumption["dashboard_surfaces"]:
        bridge_surfaces.append({
            "surface_id": surface["surface_id"],
            "fetch_path": surface["fetch_path"],
            "method": surface["method"],
            "render_mode": surface["render_mode"],
            "response_mode": surface["response_mode"],
            "panel_mount": f"s45-panel-{surface['surface_id'].replace('_', '-')}",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "autonomous_execution_enabled": False,
            "automatic_updates_enabled": False,
            "browser_execution_enabled": False,
            "javascript_execution_authority": "presentation_only",
        })

    return {
        "version": S45_VERSION,
        "phase": "S45R1-R2",
        "status": "cockpit_ui_bridge_manifest_ready",
        "bridge_surface_count": len(bridge_surfaces),
        "bridge_surfaces": bridge_surfaces,
        "source_consumption_status": consumption["status"],
        "source_plateau_status": plateau["status"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "browser_execution_enabled": False,
        "asset_root": S45_BRIDGE_ASSET_ROOT,
        "next_phase": "S45R3-R4 operator-visible panel bindings",
    }


def verify_cockpit_ui_bridge_manifest() -> dict[str, Any]:
    manifest = build_cockpit_ui_bridge_manifest()
    failures: list[str] = []

    if manifest["bridge_surface_count"] != 7:
        failures.append("bridge surface count mismatch")
    if not manifest["cockpit_presentation_only"]:
        failures.append("cockpit presentation-only flag drift")
    if manifest["runtime_truth_mutation_allowed"]:
        failures.append("runtime truth mutation allowed")

    seen_mounts: set[str] = set()
    for surface in manifest["bridge_surfaces"]:
        if surface["method"] != "GET":
            failures.append(f"{surface['surface_id']} method drift")
        if not surface["presentation_only"]:
            failures.append(f"{surface['surface_id']} presentation drift")
        if surface["runtime_truth_mutation_allowed"]:
            failures.append(f"{surface['surface_id']} runtime truth mutation drift")
        if surface["panel_mount"] in seen_mounts:
            failures.append(f"duplicate mount {surface['panel_mount']}")
        seen_mounts.add(surface["panel_mount"])

    upstream = verify_dashboard_consumption_manifest()
    if not upstream["verification_ok"]:
        failures.extend(upstream["failures"])

    return {
        "version": S45_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "bridge_surface_count": manifest["bridge_surface_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }
