from __future__ import annotations

from typing import Any

from claire.api.s44_cockpit_fetch_contracts import (
    S44_VERSION,
    build_cockpit_fetch_contracts,
    verify_cockpit_fetch_contracts,
)
from claire.api.s44_operator_payload_rendering_contracts import (
    build_operator_rendering_contracts,
    verify_operator_rendering_contracts,
)


def build_dashboard_consumption_manifest() -> dict[str, Any]:
    fetch = build_cockpit_fetch_contracts()
    rendering = build_operator_rendering_contracts()
    return {
        "version": S44_VERSION,
        "phase": "S44R5-R8",
        "status": "dashboard_consumption_manifest_ready",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "fetch_contracts": fetch,
        "rendering_contracts": rendering,
        "dashboard_surfaces": [
            {
                "surface_id": contract["surface_id"],
                "fetch_path": contract["path"],
                "method": contract["method"],
                "render_mode": "read_only_operator_card",
                "response_mode": "read_only_artifact",
                "presentation_only": True,
                "backend_owns_truth": True,
            }
            for contract in fetch["contracts"]
        ],
        "surface_count": fetch["contract_count"],
        "next_phase": "S44R9-R16 cockpit fetch verification and status aggregation",
    }


def verify_dashboard_consumption_manifest() -> dict[str, Any]:
    fetch_verify = verify_cockpit_fetch_contracts()
    render_verify = verify_operator_rendering_contracts()
    manifest = build_dashboard_consumption_manifest()

    failures: list[str] = []
    if not fetch_verify["verification_ok"]:
        failures.extend(fetch_verify["failures"])
    if not render_verify["verification_ok"]:
        failures.extend(render_verify["failures"])
    if manifest["surface_count"] != len(manifest["dashboard_surfaces"]):
        failures.append("surface count mismatch")
    for surface in manifest["dashboard_surfaces"]:
        if surface["method"] != "GET":
            failures.append(f"{surface['surface_id']} method drift")
        if not surface["presentation_only"]:
            failures.append(f"{surface['surface_id']} presentation authority drift")

    return {
        "version": S44_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "surface_count": manifest["surface_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_s44_plateau_report() -> dict[str, Any]:
    manifest = build_dashboard_consumption_manifest()
    verification = verify_dashboard_consumption_manifest()
    return {
        "version": S44_VERSION,
        "status": "s44r1_r8_ready" if verification["verification_ok"] else "blocked",
        "manifest": manifest,
        "verification": verification,
        "next_phase": manifest["next_phase"],
    }
