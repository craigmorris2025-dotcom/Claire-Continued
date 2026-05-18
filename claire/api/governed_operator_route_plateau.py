
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


def build_operator_route_plateau_index(registry: Mapping[str, Any], response_index: Mapping[str, Any]) -> Dict[str, Any]:
    responses_by_route = {row.get("route"): row for row in response_index.get("responses", []) or []}
    routes: List[Dict[str, Any]] = []
    for contract in registry.get("contracts", []) or []:
        response = responses_by_route.get(contract.get("route"), {})
        route = {
            "route": contract.get("route"),
            "method": contract.get("method"),
            "artifact": contract.get("artifact"),
            "artifact_available": response.get("artifact_available", contract.get("available", False)),
            "response_mode": contract.get("response_mode", "read_only_artifact"),
            "mutating": False,
            "route_contract_sha256": contract.get("route_contract_sha256"),
            "route_response_sha256": response.get("route_response_sha256"),
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
        }
        route["route_plateau_entry_sha256"] = _sha256(route)
        routes.append(route)

    index = {
        "record_type": "operator_route_plateau_index",
        "version": "v19.89.8-S41R13-R16",
        "route_count": len(routes),
        "available_route_artifact_count": sum(1 for route in routes if route.get("artifact_available") is True),
        "routes": routes,
        "source_route_registry_sha256": registry.get("route_registry_sha256"),
        "source_route_response_index_sha256": response_index.get("route_response_index_sha256"),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "route_wiring_installed": False,
        "created_at": _utc_now(),
    }
    index["route_plateau_index_sha256"] = _sha256(index)
    return index


def build_missing_route_artifact_registry(plateau_index: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [
        {
            "route": route.get("route"),
            "artifact": route.get("artifact"),
            "reason": "artifact_missing",
            "mutating": False,
        }
        for route in plateau_index.get("routes", []) or []
        if route.get("artifact_available") is not True
    ]
    registry = {
        "record_type": "missing_operator_route_artifact_registry",
        "version": "v19.89.8-S41R13-R16",
        "missing_count": len(missing),
        "missing_artifacts": missing,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "route_wiring_installed": False,
        "created_at": _utc_now(),
    }
    registry["missing_registry_sha256"] = _sha256(registry)
    return registry


def verify_operator_route_plateau(plateau_index: Mapping[str, Any], missing_registry: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    if plateau_index.get("runtime_truth_mutation_allowed") is not False:
        failures.append("plateau_index_runtime_truth_mutation_not_false")
    if plateau_index.get("automatic_update_allowed") is not False:
        failures.append("plateau_index_automatic_update_not_false")
    if plateau_index.get("route_wiring_installed") is not False:
        failures.append("route_wiring_unexpectedly_installed")
    if missing_registry.get("runtime_truth_mutation_allowed") is not False:
        failures.append("missing_registry_runtime_truth_mutation_not_false")
    if missing_registry.get("route_wiring_installed") is not False:
        failures.append("missing_registry_route_wiring_unexpectedly_installed")

    for route in plateau_index.get("routes", []) or []:
        if route.get("method") != "GET":
            failures.append(f"{route.get('route')}_method_not_get")
        if route.get("mutating") is not False:
            failures.append(f"{route.get('route')}_mutating_not_false")
        if route.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{route.get('route')}_runtime_truth_mutation_not_false")

    report = {
        "record_type": "operator_route_plateau_verification",
        "version": "v19.89.8-S41R13-R16",
        "verification_ok": not failures,
        "failures": failures,
        "route_count": plateau_index.get("route_count", 0),
        "missing_count": missing_registry.get("missing_count", 0),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "route_wiring_installed": False,
        "created_at": _utc_now(),
    }
    report["route_plateau_verification_sha256"] = _sha256(report)
    return report


def build_s41_route_plateau_report(
    plateau_index: Mapping[str, Any],
    missing_registry: Mapping[str, Any],
    verification: Mapping[str, Any],
) -> Dict[str, Any]:
    status = "s41_route_plateau_ready" if verification.get("verification_ok") is True else "s41_route_plateau_blocked"
    report = {
        "record_type": "s41_operator_route_plateau_report",
        "version": "v19.89.8-S41R13-R16",
        "status": status,
        "route_count": plateau_index.get("route_count", 0),
        "available_route_artifact_count": plateau_index.get("available_route_artifact_count", 0),
        "missing_route_artifact_count": missing_registry.get("missing_count", 0),
        "verification_ok": verification.get("verification_ok") is True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "route_wiring_installed": False,
        "next_phase": "S42 read-only route exposure through existing router boundary",
        "created_at": _utc_now(),
    }
    report["s41_route_plateau_report_sha256"] = _sha256(report)
    return report


def write_s41_operator_route_plateau(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = root / "output" / "operator_route_contracts"
    registry = _read_json(source_dir / "operator_route_contract_registry.json")
    response_index = _read_json(source_dir / "operator_route_response_index.json")

    plateau_index = build_operator_route_plateau_index(registry, response_index)
    missing_registry = build_missing_route_artifact_registry(plateau_index)
    verification = verify_operator_route_plateau(plateau_index, missing_registry)
    report = build_s41_route_plateau_report(plateau_index, missing_registry, verification)

    files = {
        "plateau_index": output_dir / "operator_route_plateau_index.json",
        "missing_registry": output_dir / "missing_operator_route_artifact_registry.json",
        "verification": output_dir / "operator_route_plateau_verification.json",
        "report": output_dir / "s41_operator_route_plateau_report.json",
    }
    files["plateau_index"].write_text(json.dumps(plateau_index, indent=2, sort_keys=True), encoding="utf-8")
    files["missing_registry"].write_text(json.dumps(missing_registry, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    files["report"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
