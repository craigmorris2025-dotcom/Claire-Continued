from __future__ import annotations

from typing import Any

from claire.api.s44_cockpit_fetch_contracts import (
    S44_VERSION,
    build_cockpit_fetch_contracts,
)


RENDER_MODE = "read_only_operator_card"


def build_operator_rendering_contracts() -> dict[str, Any]:
    fetch = build_cockpit_fetch_contracts()
    render_contracts = []
    for contract in fetch["contracts"]:
        render_contracts.append({
            "surface_id": contract["surface_id"],
            "source_path": contract["path"],
            "render_mode": RENDER_MODE,
            "presentation_only": True,
            "backend_owns_truth": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "autonomous_execution_enabled": False,
            "automatic_updates_enabled": False,
            "browser_execution_enabled": False,
            "javascript_execution_enabled": False,
            "empty_state": "waiting_for_backend_payload",
            "error_state": "backend_payload_unavailable",
        })
    return {
        "version": S44_VERSION,
        "phase": "S44R3-R4",
        "status": "operator_payload_rendering_contracts_ready",
        "render_mode": RENDER_MODE,
        "render_contract_count": len(render_contracts),
        "render_contracts": render_contracts,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "next_phase": "S44R5-R8 dashboard consumption manifest",
    }


def render_operator_payload(surface_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    contracts = build_operator_rendering_contracts()["render_contracts"]
    known = {contract["surface_id"]: contract for contract in contracts}
    if surface_id not in known:
        raise KeyError(surface_id)
    contract = known[surface_id]
    return {
        "version": S44_VERSION,
        "surface_id": surface_id,
        "source_path": contract["source_path"],
        "render_mode": contract["render_mode"],
        "presentation_only": True,
        "backend_owns_truth": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "payload": payload,
        "payload_status": payload.get("status", "unknown"),
    }


def verify_operator_rendering_contracts() -> dict[str, Any]:
    payload = build_operator_rendering_contracts()
    failures: list[str] = []
    for contract in payload["render_contracts"]:
        if contract["render_mode"] != RENDER_MODE:
            failures.append(f"{contract['surface_id']} render mode drift")
        if not contract["presentation_only"]:
            failures.append(f"{contract['surface_id']} is not presentation-only")
        if contract["runtime_truth_mutation_allowed"]:
            failures.append(f"{contract['surface_id']} allows runtime truth mutation")
    return {
        "version": S44_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "render_contract_count": payload["render_contract_count"],
    }
