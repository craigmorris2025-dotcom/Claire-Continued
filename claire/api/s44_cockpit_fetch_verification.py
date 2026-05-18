from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.operator_router_include_adapter import include_operator_router_non_invasive
from claire.api.s44_cockpit_fetch_contracts import (
    S44_VERSION,
    build_cockpit_fetch_contracts,
)


S44_R9_R16_VERSION = "v19.89.8-S44R9-R16"


def build_cockpit_fetch_verification_app() -> FastAPI:
    app = FastAPI()
    include_operator_router_non_invasive(app)
    return app


def verify_cockpit_fetch_contract_responses(app: FastAPI | None = None) -> dict[str, Any]:
    app = app or build_cockpit_fetch_verification_app()
    client = TestClient(app)
    contracts = build_cockpit_fetch_contracts()["contracts"]

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for contract in contracts:
        response = client.get(contract["path"])
        try:
            body = response.json()
        except Exception:
            body = {"raw": response.text}

        item = {
            "surface_id": contract["surface_id"],
            "path": contract["path"],
            "method": contract["method"],
            "expected_status": contract["expected_status"],
            "status_code": response.status_code,
            "available": response.status_code == contract["expected_status"],
            "read_only": True,
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "automatic_update_allowed": False,
            "response_mode": "read_only_artifact",
            "body_status": body.get("status"),
        }
        if not item["available"]:
            failures.append({
                "surface_id": contract["surface_id"],
                "path": contract["path"],
                "expected_status": contract["expected_status"],
                "status_code": response.status_code,
            })
        results.append(item)

    ok_count = sum(1 for item in results if item["available"])

    return {
        "version": S44_R9_R16_VERSION,
        "phase": "S44R9-R10",
        "status": "cockpit_fetch_verification_ready",
        "contract_version": S44_VERSION,
        "probe_count": len(results),
        "ok_count": ok_count,
        "available_count": ok_count,
        "failure_count": len(failures),
        "results": results,
        "failures": failures,
        "verification_ok": failures == [],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "live_server_required": False,
        "next_phase": "S44R11-R12 cockpit status aggregation",
    }


def verify_cockpit_fetch_contracts_live() -> dict[str, Any]:
    return verify_cockpit_fetch_contract_responses()


def build_cockpit_fetch_verification_summary() -> dict[str, Any]:
    verification = verify_cockpit_fetch_contract_responses()
    return {
        "version": S44_R9_R16_VERSION,
        "status": "all_fetch_contracts_available" if verification["verification_ok"] else "fetch_contract_failure",
        "verification_ok": verification["verification_ok"],
        "probe_count": verification["probe_count"],
        "ok_count": verification["ok_count"],
        "failure_count": verification["failure_count"],
        "runtime_truth_mutation_allowed": False,
        "cockpit_presentation_only": True,
    }
