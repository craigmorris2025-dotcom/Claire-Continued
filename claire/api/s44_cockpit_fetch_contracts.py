from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


S44_VERSION = "v19.89.8-S44R1-R8"


@dataclass(frozen=True)
class CockpitFetchContract:
    surface_id: str
    path: str
    method: str = "GET"
    expected_status: int = 200
    backend_owns_truth: bool = True
    cockpit_presentation_only: bool = True
    read_only: bool = True
    runtime_truth_mutation_allowed: bool = False
    runtime_mutation_allowed: bool = False
    operator_mutation_enabled: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    browser_execution_enabled: bool = False
    javascript_execution_enabled: bool = False
    live_server_required: bool = False
    response_mode: str = "read_only_artifact"


S44_OPERATOR_FETCH_CONTRACTS: tuple[CockpitFetchContract, ...] = (
    CockpitFetchContract("operator_payload", "/operator/payload"),
    CockpitFetchContract("operator_routes", "/operator/routes"),
    CockpitFetchContract("operator_runtime_status", "/operator/runtime/status"),
    CockpitFetchContract("operator_evidence_review", "/operator/evidence/review"),
    CockpitFetchContract("operator_evidence_status", "/operator/evidence/status"),
    CockpitFetchContract("operator_review_status", "/operator/review/status"),
    CockpitFetchContract("operator_routes_status", "/operator/routes/status"),
)


def build_cockpit_fetch_contracts() -> dict[str, Any]:
    contracts = [asdict(contract) for contract in S44_OPERATOR_FETCH_CONTRACTS]
    return {
        "version": S44_VERSION,
        "phase": "S44R1-R2",
        "status": "cockpit_fetch_contracts_ready",
        "contract_count": len(contracts),
        "contracts": contracts,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "browser_execution_enabled": False,
        "javascript_execution_enabled": False,
        "live_server_required": False,
        "next_phase": "S44R3-R4 operator payload rendering contracts",
    }


def get_contract_by_surface(surface_id: str) -> dict[str, Any]:
    for contract in S44_OPERATOR_FETCH_CONTRACTS:
        if contract.surface_id == surface_id:
            return asdict(contract)
    raise KeyError(surface_id)


def list_contract_paths() -> list[str]:
    return [contract.path for contract in S44_OPERATOR_FETCH_CONTRACTS]


def verify_cockpit_fetch_contracts() -> dict[str, Any]:
    payload = build_cockpit_fetch_contracts()
    failures: list[str] = []
    seen_paths: set[str] = set()
    for contract in payload["contracts"]:
        if contract["method"] != "GET":
            failures.append(f"{contract['surface_id']} method is not GET")
        if not contract["read_only"]:
            failures.append(f"{contract['surface_id']} is not read-only")
        if contract["runtime_truth_mutation_allowed"]:
            failures.append(f"{contract['surface_id']} allows runtime truth mutation")
        if contract["path"] in seen_paths:
            failures.append(f"duplicate path {contract['path']}")
        seen_paths.add(contract["path"])
    return {
        "version": S44_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "contract_count": payload["contract_count"],
        "paths": sorted(seen_paths),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
    }
