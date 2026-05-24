from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from runtime_core.api.operator_router_include_adapter import include_operator_router_non_invasive
from runtime_core.api.s45_cockpit_shell_bridge import (
    S45_R9_R16_VERSION,
    build_cockpit_shell_bridge_manifest,
)


def build_panel_data_mounting_contracts() -> dict[str, Any]:
    shell = build_cockpit_shell_bridge_manifest()
    contracts = []
    for mount in shell["shell_mounts"]:
        contracts.append({
            "mount_id": mount["mount_id"],
            "surface_id": mount["surface_id"],
            "fetch_path": mount["fetch_path"],
            "method": "GET",
            "expected_status": 200,
            "mount_state": "mounted",
            "data_state": "awaiting_fetch",
            "render_state": "ready_for_payload",
            "response_mode": "read_only_artifact",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
            "failure_state": "show_unavailable_card",
            "empty_state": "waiting_for_backend_payload",
        })

    return {
        "version": S45_R9_R16_VERSION,
        "phase": "S45R11-R12",
        "status": "panel_data_mounting_contracts_ready",
        "contract_count": len(contracts),
        "contracts": contracts,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "next_phase": "S45R13-R16 shell-mounted data probe",
    }


def build_panel_mount_test_app() -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app)
    return app


def probe_panel_data_mounts(app: FastAPI | None = None) -> dict[str, Any]:
    app = app or build_panel_mount_test_app()
    client = TestClient(app)
    contracts = build_panel_data_mounting_contracts()["contracts"]

    results = []
    failures = []

    for contract in contracts:
        response = client.get(contract["fetch_path"])
        ok = response.status_code == contract["expected_status"]
        item = {
            "mount_id": contract["mount_id"],
            "surface_id": contract["surface_id"],
            "fetch_path": contract["fetch_path"],
            "status_code": response.status_code,
            "available": ok,
            "mounted": True,
            "renderable": ok,
            "read_only": True,
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "response_mode": "read_only_artifact",
        }
        if not ok:
            failures.append({
                "mount_id": contract["mount_id"],
                "fetch_path": contract["fetch_path"],
                "status_code": response.status_code,
            })
        results.append(item)

    ok_count = sum(1 for item in results if item["available"])

    return {
        "version": S45_R9_R16_VERSION,
        "phase": "S45R13-R14",
        "status": "panel_data_mount_probe_ready",
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "failure_count": len(failures),
        "results": results,
        "failures": failures,
        "verification_ok": failures == [],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "live_server_required": False,
    }


def build_s45r9_r16_plateau_report() -> dict[str, Any]:
    shell = build_cockpit_shell_bridge_manifest()
    contracts = build_panel_data_mounting_contracts()
    probe = probe_panel_data_mounts()
    failures = list(probe["failures"])
    ready = failures == []

    return {
        "version": S45_R9_R16_VERSION,
        "phase": "S45R15-R16",
        "status": "s45r9_r16_ready" if ready else "s45r9_r16_blocked",
        "ready": ready,
        "shell": shell,
        "contracts": contracts,
        "probe": probe,
        "failures": failures,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S46 modern cockpit layout consolidation and live status zones",
    }
