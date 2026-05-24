
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


ROUTE_CONTRACTS = [
    {
        "route": "/operator/payload",
        "method": "GET",
        "artifact": "output/unified_operator_payload/unified_backend_operator_payload.json",
        "purpose": "read unified backend operator payload",
    },
    {
        "route": "/operator/snapshot",
        "method": "GET",
        "artifact": "output/operator_runtime_snapshots/operator_state_snapshot.json",
        "purpose": "read current operator state snapshot",
    },
    {
        "route": "/operator/summary",
        "method": "GET",
        "artifact": "output/operator_runtime_snapshots/bounded_runtime_summary.json",
        "purpose": "read bounded runtime summary",
    },
    {
        "route": "/operator/digest",
        "method": "GET",
        "artifact": "output/operator_state_digest/operator_current_state_digest.json",
        "purpose": "read current operator state digest",
    },
    {
        "route": "/operator/alerts",
        "method": "GET",
        "artifact": "output/operator_state_digest/operator_alert_summary.json",
        "purpose": "read operator alert summary",
    },
    {
        "route": "/operator/readiness",
        "method": "GET",
        "artifact": "output/operator_state_digest/s41_operator_runtime_snapshot_readiness_report.json",
        "purpose": "read S41 readiness report",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path), "reason": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("available", True)
            data.setdefault("path", str(path))
            return data
        return {"available": True, "path": str(path), "value": data}
    except Exception as exc:
        return {"available": False, "path": str(path), "reason": f"unreadable:{type(exc).__name__}"}


def build_operator_route_contract_registry(root: Path) -> Dict[str, Any]:
    contracts: List[Dict[str, Any]] = []
    for item in ROUTE_CONTRACTS:
        artifact_path = root / item["artifact"]
        available = artifact_path.exists()
        contract = {
            "route": item["route"],
            "method": item["method"],
            "artifact": item["artifact"],
            "purpose": item["purpose"],
            "available": available,
            "response_mode": "read_only_artifact",
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "browser_execution_allowed": False,
            "javascript_execution_allowed": False,
            "authority": dict(LOCKED_AUTHORITY),
        }
        contract["route_contract_sha256"] = _sha256(contract)
        contracts.append(contract)

    registry = {
        "record_type": "operator_route_contract_registry",
        "version": "v19.89.8-S41R9-R12",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "route_count": len(contracts),
        "available_route_artifact_count": sum(1 for c in contracts if c.get("available") is True),
        "contracts": contracts,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    registry["route_registry_sha256"] = _sha256(registry)
    return registry


def build_operator_route_response_index(root: Path, registry: Mapping[str, Any]) -> Dict[str, Any]:
    responses = []
    for contract in registry.get("contracts", []) or []:
        artifact = _read_json(root / str(contract.get("artifact", "")))
        response = {
            "route": contract.get("route"),
            "method": contract.get("method"),
            "artifact": contract.get("artifact"),
            "artifact_available": artifact.get("available", False),
            "artifact_record_type": artifact.get("record_type"),
            "artifact_status": artifact.get("status"),
            "artifact_reason": artifact.get("reason"),
            "route_contract_sha256": contract.get("route_contract_sha256"),
            "response_mode": "read_only_artifact",
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
        }
        response["route_response_sha256"] = _sha256(response)
        responses.append(response)

    index = {
        "record_type": "operator_route_response_index",
        "version": "v19.89.8-S41R9-R12",
        "route_response_count": len(responses),
        "responses": responses,
        "source_route_registry_sha256": registry.get("route_registry_sha256"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    index["route_response_index_sha256"] = _sha256(index)
    return index


def verify_operator_route_contracts(registry: Mapping[str, Any], response_index: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    if registry.get("runtime_truth_mutation_allowed") is not False:
        failures.append("registry_runtime_truth_mutation_not_false")
    if registry.get("automatic_update_allowed") is not False:
        failures.append("registry_automatic_update_not_false")
    if response_index.get("runtime_truth_mutation_allowed") is not False:
        failures.append("response_index_runtime_truth_mutation_not_false")
    if response_index.get("source_route_registry_sha256") != registry.get("route_registry_sha256"):
        failures.append("response_index_registry_sha_mismatch")

    routes = [contract.get("route") for contract in registry.get("contracts", []) or []]
    if len(routes) != len(set(routes)):
        failures.append("duplicate_operator_routes")

    for contract in registry.get("contracts", []) or []:
        if contract.get("mutating") is not False:
            failures.append(f"{contract.get('route')}_mutating_not_false")
        if contract.get("method") != "GET":
            failures.append(f"{contract.get('route')}_method_not_get")
        if contract.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{contract.get('route')}_runtime_mutation_not_false")
        if contract.get("automatic_update_allowed") is not False:
            failures.append(f"{contract.get('route')}_automatic_update_not_false")

    report = {
        "record_type": "operator_route_contract_verification",
        "version": "v19.89.8-S41R9-R12",
        "verification_ok": not failures,
        "failures": failures,
        "route_count": registry.get("route_count", 0),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def write_operator_route_contracts(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    registry = build_operator_route_contract_registry(root)
    response_index = build_operator_route_response_index(root, registry)
    verification = verify_operator_route_contracts(registry, response_index)

    files = {
        "registry": output_dir / "operator_route_contract_registry.json",
        "response_index": output_dir / "operator_route_response_index.json",
        "verification": output_dir / "operator_route_contract_verification.json",
    }
    files["registry"].write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    files["response_index"].write_text(json.dumps(response_index, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
