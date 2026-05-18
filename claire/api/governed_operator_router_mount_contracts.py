
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


EXPECTED_ROUTES = [
    "/operator/payload",
    "/operator/snapshot",
    "/operator/summary",
    "/operator/digest",
    "/operator/alerts",
    "/operator/readiness",
    "/operator/routes",
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


def build_operator_mount_contract(router_manifest: Mapping[str, Any], route_plateau: Mapping[str, Any]) -> Dict[str, Any]:
    manifest_routes = {route.get("route"): route for route in router_manifest.get("routes", []) or []}
    plateau_routes = {route.get("route"): route for route in route_plateau.get("routes", []) or []}

    routes: List[Dict[str, Any]] = []
    for route_name in EXPECTED_ROUTES:
        manifest = manifest_routes.get(route_name, {})
        plateau = plateau_routes.get(route_name, {})
        entry = {
            "route": route_name,
            "method": manifest.get("method", plateau.get("method", "GET")),
            "manifest_present": bool(manifest),
            "plateau_present": bool(plateau),
            "artifact": manifest.get("artifact", plateau.get("artifact")),
            "mount_allowed": bool(manifest) and str(manifest.get("method", "GET")) == "GET",
            "mount_mode": "read_only_router_include",
            "requires_app_py_patch": False,
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "browser_execution_allowed": False,
            "javascript_execution_allowed": False,
        }
        entry["mount_entry_sha256"] = _sha256(entry)
        routes.append(entry)

    contract = {
        "record_type": "operator_router_mount_contract",
        "version": "v19.89.8-S42R5-R12",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "route_count": len(routes),
        "mount_allowed_count": sum(1 for route in routes if route.get("mount_allowed") is True),
        "routes": routes,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "requires_app_py_patch": False,
        "created_at": _utc_now(),
    }
    contract["mount_contract_sha256"] = _sha256(contract)
    return contract


def build_operator_route_probe_plan(mount_contract: Mapping[str, Any]) -> Dict[str, Any]:
    probes = []
    for route in mount_contract.get("routes", []) or []:
        probes.append({
            "route": route.get("route"),
            "method": "GET",
            "expected_status": 200,
            "expected_response_mode": "read_only_artifact",
            "allowed_to_execute_live": False,
            "probe_type": "contract_only_until_router_mounted",
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
        })

    plan = {
        "record_type": "operator_route_probe_plan",
        "version": "v19.89.8-S42R5-R12",
        "probe_count": len(probes),
        "probes": probes,
        "live_execution_allowed": False,
        "contract_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    plan["probe_plan_sha256"] = _sha256(plan)
    return plan


def build_operator_router_mount_readiness(mount_contract: Mapping[str, Any], probe_plan: Mapping[str, Any]) -> Dict[str, Any]:
    blocked_reasons: List[str] = []
    if mount_contract.get("requires_app_py_patch") is not False:
        blocked_reasons.append("app_py_patch_required")
    if mount_contract.get("runtime_truth_mutation_allowed") is not False:
        blocked_reasons.append("runtime_truth_mutation_not_locked")
    if probe_plan.get("live_execution_allowed") is not False:
        blocked_reasons.append("live_probe_execution_unexpectedly_allowed")
    for route in mount_contract.get("routes", []) or []:
        if route.get("method") != "GET":
            blocked_reasons.append(f"{route.get('route')}_method_not_get")
        if route.get("mutating") is not False:
            blocked_reasons.append(f"{route.get('route')}_mutating_not_false")

    readiness = {
        "record_type": "operator_router_mount_readiness",
        "version": "v19.89.8-S42R5-R12",
        "status": "mount_contract_ready" if not blocked_reasons else "mount_contract_blocked",
        "blocked_reasons": blocked_reasons,
        "route_count": mount_contract.get("route_count", 0),
        "mount_allowed_count": mount_contract.get("mount_allowed_count", 0),
        "source_mount_contract_sha256": mount_contract.get("mount_contract_sha256"),
        "source_probe_plan_sha256": probe_plan.get("probe_plan_sha256"),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "requires_app_py_patch": False,
        "created_at": _utc_now(),
    }
    readiness["mount_readiness_sha256"] = _sha256(readiness)
    return readiness


def verify_operator_router_mount_contracts(
    mount_contract: Mapping[str, Any],
    probe_plan: Mapping[str, Any],
    readiness: Mapping[str, Any],
) -> Dict[str, Any]:
    failures: List[str] = []

    for name, payload in {
        "mount_contract": mount_contract,
        "probe_plan": probe_plan,
        "readiness": readiness,
    }.items():
        if payload.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{name}_runtime_truth_mutation_not_false")
        if payload.get("automatic_update_allowed") is not False:
            failures.append(f"{name}_automatic_update_not_false")

    if mount_contract.get("requires_app_py_patch") is not False:
        failures.append("mount_contract_requires_app_py_patch")
    if probe_plan.get("live_execution_allowed") is not False:
        failures.append("probe_plan_live_execution_not_false")
    if readiness.get("source_mount_contract_sha256") != mount_contract.get("mount_contract_sha256"):
        failures.append("readiness_mount_contract_sha_mismatch")
    if readiness.get("source_probe_plan_sha256") != probe_plan.get("probe_plan_sha256"):
        failures.append("readiness_probe_plan_sha_mismatch")
    if [route.get("route") for route in mount_contract.get("routes", []) or []] != EXPECTED_ROUTES:
        failures.append("mount_contract_route_order_mismatch")

    report = {
        "record_type": "operator_router_mount_contract_verification",
        "version": "v19.89.8-S42R5-R12",
        "verification_ok": not failures,
        "failures": failures,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "requires_app_py_patch": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def build_s42_mount_plateau_report(readiness: Mapping[str, Any], verification: Mapping[str, Any]) -> Dict[str, Any]:
    status = "s42_mount_contract_plateau_ready" if verification.get("verification_ok") and readiness.get("status") == "mount_contract_ready" else "s42_mount_contract_blocked"
    report = {
        "record_type": "s42_operator_mount_contract_plateau_report",
        "version": "v19.89.8-S42R5-R12",
        "status": status,
        "verification_ok": verification.get("verification_ok") is True,
        "mount_readiness_status": readiness.get("status"),
        "route_count": readiness.get("route_count", 0),
        "mount_allowed_count": readiness.get("mount_allowed_count", 0),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "requires_app_py_patch": False,
        "next_phase": "S42R13-R16 app factory discovery and non-invasive router include adapter",
        "created_at": _utc_now(),
    }
    report["s42_mount_plateau_report_sha256"] = _sha256(report)
    return report


def write_operator_router_mount_contracts(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    router_manifest = _read_json(root / "output" / "operator_read_only_router" / "operator_read_only_router_manifest.json")
    route_plateau = _read_json(root / "output" / "operator_route_plateau" / "operator_route_plateau_index.json")

    mount_contract = build_operator_mount_contract(router_manifest, route_plateau)
    probe_plan = build_operator_route_probe_plan(mount_contract)
    readiness = build_operator_router_mount_readiness(mount_contract, probe_plan)
    verification = verify_operator_router_mount_contracts(mount_contract, probe_plan, readiness)
    report = build_s42_mount_plateau_report(readiness, verification)

    files = {
        "mount_contract": output_dir / "operator_router_mount_contract.json",
        "probe_plan": output_dir / "operator_route_probe_plan.json",
        "readiness": output_dir / "operator_router_mount_readiness.json",
        "verification": output_dir / "operator_router_mount_contract_verification.json",
        "report": output_dir / "s42_operator_mount_contract_plateau_report.json",
    }
    files["mount_contract"].write_text(json.dumps(mount_contract, indent=2, sort_keys=True), encoding="utf-8")
    files["probe_plan"].write_text(json.dumps(probe_plan, indent=2, sort_keys=True), encoding="utf-8")
    files["readiness"].write_text(json.dumps(readiness, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    files["report"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
