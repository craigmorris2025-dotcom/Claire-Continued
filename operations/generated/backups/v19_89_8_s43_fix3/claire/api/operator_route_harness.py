
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping

from fastapi import FastAPI
from fastapi.testclient import TestClient

from claire.api.operator_router_include_adapter import include_operator_router_non_invasive


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


def build_isolated_operator_route_test_app(root: Path) -> FastAPI:
    app = FastAPI(title="Claire Operator Route Harness")
    include_operator_router_non_invasive(app, root=root)
    return app


def probe_operator_routes_isolated(root: Path) -> Dict[str, Any]:
    app = build_isolated_operator_route_test_app(root)
    client = TestClient(app)
    results: List[Dict[str, Any]] = []

    for route in EXPECTED_ROUTES:
        response = client.get(route)
        body: Dict[str, Any]
        try:
            body = response.json()
        except Exception as exc:
            body = {"available": False, "reason": f"invalid_json:{type(exc).__name__}"}

        result = {
            "route": route,
            "status_code": response.status_code,
            "ok": response.status_code == 200,
            "available": body.get("available"),
            "response_mode": body.get("response_mode"),
            "mutating": body.get("mutating"),
            "runtime_truth_mutation_allowed": body.get("runtime_truth_mutation_allowed"),
            "automatic_update_allowed": body.get("automatic_update_allowed"),
            "browser_execution_allowed": body.get("browser_execution_allowed"),
            "javascript_execution_allowed": body.get("javascript_execution_allowed"),
            "artifact": body.get("artifact"),
            "payload_record_type": (body.get("payload") or {}).get("record_type") if isinstance(body.get("payload"), dict) else None,
        }
        result["route_probe_sha256"] = _sha256(result)
        results.append(result)

    report = {
        "record_type": "isolated_operator_route_probe_report",
        "version": "v19.89.8-S42R21-R28",
        "probe_count": len(results),
        "ok_count": sum(1 for item in results if item.get("ok") is True),
        "available_count": sum(1 for item in results if item.get("available") is True),
        "results": results,
        "isolated_test_app": True,
        "app_py_patch_required": False,
        "live_server_required": False,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["probe_report_sha256"] = _sha256(report)
    return report


def verify_isolated_operator_route_probe(probe_report: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []

    if probe_report.get("app_py_patch_required") is not False:
        failures.append("app_py_patch_required")
    if probe_report.get("live_server_required") is not False:
        failures.append("live_server_required")
    if probe_report.get("runtime_truth_mutation_allowed") is not False:
        failures.append("probe_report_runtime_truth_mutation_not_false")
    if probe_report.get("automatic_update_allowed") is not False:
        failures.append("probe_report_automatic_update_not_false")

    routes = [item.get("route") for item in probe_report.get("results", []) or []]
    if routes != EXPECTED_ROUTES:
        failures.append("route_order_mismatch")

    for item in probe_report.get("results", []) or []:
        route = item.get("route")
        if item.get("status_code") != 200:
            failures.append(f"{route}_status_not_200")
        if item.get("mutating") is not False:
            failures.append(f"{route}_mutating_not_false")
        if item.get("response_mode") != "read_only_artifact":
            failures.append(f"{route}_response_mode_not_read_only_artifact")
        if item.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{route}_runtime_truth_mutation_not_false")
        if item.get("automatic_update_allowed") is not False:
            failures.append(f"{route}_automatic_update_not_false")
        if item.get("browser_execution_allowed") is not False:
            failures.append(f"{route}_browser_execution_not_false")
        if item.get("javascript_execution_allowed") is not False:
            failures.append(f"{route}_javascript_execution_not_false")

    verification = {
        "record_type": "isolated_operator_route_probe_verification",
        "version": "v19.89.8-S42R21-R28",
        "verification_ok": not failures,
        "failures": failures,
        "probe_count": probe_report.get("probe_count", 0),
        "ok_count": probe_report.get("ok_count", 0),
        "source_probe_report_sha256": probe_report.get("probe_report_sha256"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "app_py_patch_required": False,
        "created_at": _utc_now(),
    }
    verification["verification_sha256"] = _sha256(verification)
    return verification


def build_s42_route_harness_plateau(probe_report: Mapping[str, Any], verification: Mapping[str, Any]) -> Dict[str, Any]:
    status = "s42_route_harness_ready" if verification.get("verification_ok") is True else "s42_route_harness_blocked"
    plateau = {
        "record_type": "s42_operator_route_harness_plateau_report",
        "version": "v19.89.8-S42R21-R28",
        "status": status,
        "verification_ok": verification.get("verification_ok") is True,
        "probe_count": probe_report.get("probe_count", 0),
        "ok_count": probe_report.get("ok_count", 0),
        "available_count": probe_report.get("available_count", 0),
        "isolated_test_app": True,
        "app_py_patch_required": False,
        "live_server_required": False,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "next_phase": "S43 controlled app integration discovery and mounted-route availability verification",
        "created_at": _utc_now(),
    }
    plateau["route_harness_plateau_sha256"] = _sha256(plateau)
    return plateau


def write_s42_live_route_harness(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    probe_report = probe_operator_routes_isolated(root)
    verification = verify_isolated_operator_route_probe(probe_report)
    plateau = build_s42_route_harness_plateau(probe_report, verification)

    files = {
        "probe_report": output_dir / "isolated_operator_route_probe_report.json",
        "verification": output_dir / "isolated_operator_route_probe_verification.json",
        "plateau": output_dir / "s42_operator_route_harness_plateau_report.json",
    }
    files["probe_report"].write_text(json.dumps(probe_report, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    files["plateau"].write_text(json.dumps(plateau, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
