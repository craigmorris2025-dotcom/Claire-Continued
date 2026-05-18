
from __future__ import annotations

import hashlib
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

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


def discover_primary_app() -> Dict[str, Any]:
    attempts: List[Dict[str, Any]] = []
    selected: Optional[Dict[str, Any]] = None

    candidates = [("claire.app", "create_app"), ("main", "app")]
    for module_name, attr_name in candidates:
        attempt = {
            "module": module_name,
            "attribute": attr_name,
            "available": False,
            "usable": False,
            "kind": None,
            "reason": None,
        }
        try:
            module = importlib.import_module(module_name)
            obj = getattr(module, attr_name)
            if callable(obj):
                app = obj()
                attempt["kind"] = "factory"
            else:
                app = obj
                attempt["kind"] = "app_object"
            attempt["available"] = True
            attempt["usable"] = isinstance(app, FastAPI)
            if attempt["usable"] and selected is None:
                selected = {
                    "module": module_name,
                    "attribute": attr_name,
                    "kind": attempt["kind"],
                }
        except Exception as exc:
            attempt["reason"] = f"{type(exc).__name__}:{exc}"
        attempts.append(attempt)

    report = {
        "record_type": "primary_app_discovery_report",
        "version": "v19.89.8-S43R1-R8",
        "selected": selected,
        "attempts": attempts,
        "app_py_patch_required": False,
        "non_invasive": True,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "authority": dict(LOCKED_AUTHORITY),
        "created_at": _utc_now(),
    }
    report["discovery_sha256"] = _sha256(report)
    return report


def create_mounted_app_from_discovery(root: Path) -> FastAPI:
    discovery = discover_primary_app()
    selected = discovery.get("selected")
    if selected:
        module = importlib.import_module(str(selected["module"]))
        obj = getattr(module, str(selected["attribute"]))
        app = obj() if callable(obj) else obj
        if not isinstance(app, FastAPI):
            app = FastAPI(title="Claire Controlled Mount Fallback")
    else:
        app = FastAPI(title="Claire Controlled Mount Fallback")
    include_operator_router_non_invasive(app, root=root)
    return app


def probe_mounted_operator_routes(root: Path) -> Dict[str, Any]:
    app = create_mounted_app_from_discovery(root)
    client = TestClient(app)
    results: List[Dict[str, Any]] = []

    for route in EXPECTED_ROUTES:
        response = client.get(route)
        try:
            body = response.json()
        except Exception as exc:
            body = {"reason": f"invalid_json:{type(exc).__name__}"}
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
        }
        result["mounted_route_probe_sha256"] = _sha256(result)
        results.append(result)

    report = {
        "record_type": "mounted_operator_route_probe_report",
        "version": "v19.89.8-S43R1-R8",
        "probe_count": len(results),
        "ok_count": sum(1 for item in results if item.get("ok") is True),
        "available_count": sum(1 for item in results if item.get("available") is True),
        "results": results,
        "app_py_patch_required": False,
        "live_server_required": False,
        "non_invasive_mount": True,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "authority": dict(LOCKED_AUTHORITY),
        "created_at": _utc_now(),
    }
    report["mounted_probe_report_sha256"] = _sha256(report)
    return report


def verify_mounted_operator_routes(discovery: Mapping[str, Any], probe_report: Mapping[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    if discovery.get("app_py_patch_required") is not False:
        failures.append("discovery_requires_app_py_patch")
    if probe_report.get("app_py_patch_required") is not False:
        failures.append("probe_requires_app_py_patch")
    if probe_report.get("runtime_truth_mutation_allowed") is not False:
        failures.append("probe_runtime_truth_mutation_not_false")
    if probe_report.get("automatic_update_allowed") is not False:
        failures.append("probe_automatic_update_not_false")

    if [item.get("route") for item in probe_report.get("results", []) or []] != EXPECTED_ROUTES:
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

    verification = {
        "record_type": "mounted_operator_route_verification",
        "version": "v19.89.8-S43R1-R8",
        "verification_ok": not failures,
        "failures": failures,
        "source_discovery_sha256": discovery.get("discovery_sha256"),
        "source_probe_report_sha256": probe_report.get("mounted_probe_report_sha256"),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "app_py_patch_required": False,
        "created_at": _utc_now(),
    }
    verification["verification_sha256"] = _sha256(verification)
    return verification


def build_s43_app_integration_report(discovery: Mapping[str, Any], probe_report: Mapping[str, Any], verification: Mapping[str, Any]) -> Dict[str, Any]:
    report = {
        "record_type": "s43_app_integration_probe_report",
        "version": "v19.89.8-S43R1-R8",
        "status": "s43_app_integration_probe_ready" if verification.get("verification_ok") is True else "s43_app_integration_probe_blocked",
        "selected_app": discovery.get("selected"),
        "probe_count": probe_report.get("probe_count", 0),
        "ok_count": probe_report.get("ok_count", 0),
        "available_count": probe_report.get("available_count", 0),
        "verification_ok": verification.get("verification_ok") is True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "app_py_patch_required": False,
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "authority": dict(LOCKED_AUTHORITY),
        "next_phase": "S43R9-R16 app route exposure adapter and swagger-visible route registration plan",
        "created_at": _utc_now(),
    }
    report["s43_app_integration_report_sha256"] = _sha256(report)
    return report


def write_s43_app_integration_probe(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    discovery = discover_primary_app()
    probe = probe_mounted_operator_routes(root)
    verification = verify_mounted_operator_routes(discovery, probe)
    report = build_s43_app_integration_report(discovery, probe, verification)

    files = {
        "discovery": output_dir / "primary_app_discovery_report.json",
        "probe": output_dir / "mounted_operator_route_probe_report.json",
        "verification": output_dir / "mounted_operator_route_verification.json",
        "report": output_dir / "s43_app_integration_probe_report.json",
    }
    files["discovery"].write_text(json.dumps(discovery, indent=2, sort_keys=True), encoding="utf-8")
    files["probe"].write_text(json.dumps(probe, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    files["report"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
