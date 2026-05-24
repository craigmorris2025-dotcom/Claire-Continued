from __future__ import annotations

from typing import Any

from runtime_core.api.s44_cockpit_fetch_verification import (
    S44_R9_R16_VERSION,
    verify_cockpit_fetch_contract_responses,
)
from runtime_core.api.s44_dashboard_consumption_manifest import (
    build_dashboard_consumption_manifest,
    verify_dashboard_consumption_manifest,
)


def build_cockpit_status_aggregation() -> dict[str, Any]:
    manifest = build_dashboard_consumption_manifest()
    manifest_verification = verify_dashboard_consumption_manifest()
    fetch_verification = verify_cockpit_fetch_contract_responses()

    failures: list[Any] = []
    if not manifest_verification["verification_ok"]:
        failures.extend(manifest_verification["failures"])
    if not fetch_verification["verification_ok"]:
        failures.extend(fetch_verification["failures"])

    ready = failures == []

    return {
        "version": S44_R9_R16_VERSION,
        "phase": "S44R11-R12",
        "status": "cockpit_status_aggregation_ready" if ready else "cockpit_status_aggregation_blocked",
        "ready": ready,
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
        "surface_count": manifest["surface_count"],
        "available_count": fetch_verification["available_count"],
        "failure_count": len(failures),
        "failures": failures,
        "fetch_verification": fetch_verification,
        "manifest_verification": manifest_verification,
        "next_phase": "S44R13-R14 cockpit surface health snapshot",
    }


def build_cockpit_status_tiles() -> dict[str, Any]:
    aggregation = build_cockpit_status_aggregation()
    tiles = [
        {
            "tile_id": "backend_truth",
            "label": "Backend Truth",
            "state": "locked",
            "presentation_only": True,
            "runtime_truth_mutation_allowed": False,
        },
        {
            "tile_id": "operator_surfaces",
            "label": "Operator Surfaces",
            "state": "available" if aggregation["ready"] else "blocked",
            "available_count": aggregation["available_count"],
            "surface_count": aggregation["surface_count"],
            "presentation_only": True,
            "runtime_truth_mutation_allowed": False,
        },
        {
            "tile_id": "authority",
            "label": "Authority",
            "state": "blocked",
            "operator_mutation_enabled": False,
            "autonomous_execution_enabled": False,
            "automatic_updates_enabled": False,
            "presentation_only": True,
        },
    ]
    return {
        "version": S44_R9_R16_VERSION,
        "phase": "S44R11-R12",
        "status": "cockpit_status_tiles_ready",
        "tile_count": len(tiles),
        "tiles": tiles,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
    }
