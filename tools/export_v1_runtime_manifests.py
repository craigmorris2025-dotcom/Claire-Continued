from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from runtime_core.app import create_app
from runtime_core.api.industry_standard_endpoint_package import build_standards_control_map
from runtime_core.pipeline.activation_registry import build_pipeline_activation_registry


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def active_endpoints(app: Any) -> dict[str, Any]:
    rows = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        if not path or not methods:
            continue
        endpoint = getattr(route, "endpoint", None)
        rows.append(
            {
                "path": path,
                "methods": methods,
                "name": getattr(route, "name", ""),
                "module": getattr(endpoint, "__module__", ""),
                "endpoint": getattr(endpoint, "__name__", ""),
            }
        )
    return {
        "schema_version": "claire.v1.active_endpoints.v1",
        "active_app": "main.py -> runtime_core.app:create_app",
        "route_count": len(rows),
        "endpoints": sorted(rows, key=lambda item: (item["path"], ",".join(item["methods"]))),
    }


def route_contract_test_gate_map() -> dict[str, Any]:
    registry = build_pipeline_activation_registry()
    rows = []
    for item in registry["items"]:
        rows.append(
            {
                "pipeline": item["id"],
                "owner_file": item["owner_file"],
                "route": item["route"],
                "trigger": item["trigger"],
                "score": item["score"],
                "sequence": item["sequence"],
                "output": item["output"],
                "failure_state": item["failure_state"],
                "test": "tests/test_pipeline_activation_registry.py",
                "governance_gate": "ACS2 trigger-score-route map; dashboard render only; runtime truth mutation blocked",
            }
        )
    return {
        "schema_version": "claire.v1.route_contract_test_gate_map.v1",
        "status": "ready",
        "pipeline_count": len(rows),
        "routes": rows,
    }


def dashboard_backend_route_manifest(client: TestClient) -> dict[str, Any]:
    dashboard = client.get("/api/dashboard/state").json()
    controls = dashboard.get("active_control_map", {}).get("controls", [])
    endpoints = []
    if isinstance(controls, list):
        for control in controls:
            if not isinstance(control, dict):
                continue
            endpoints.append(
                {
                    "control_id": control.get("id") or control.get("key"),
                    "label": control.get("label") or control.get("title"),
                    "primary_endpoint": control.get("primary_endpoint"),
                    "secondary_endpoints": control.get("secondary_endpoints", []),
                    "authority": control.get("authority") or control.get("mode"),
                }
            )
    return {
        "schema_version": "claire.v1.dashboard_backend_route_manifest.v1",
        "status": dashboard.get("status", "ready"),
        "dashboard_route": "/dashboard",
        "dashboard_state_endpoint": "/api/dashboard/state",
        "active_control_endpoint": "/api/dashboard/active-control-map",
        "control_count": len(endpoints),
        "controls": endpoints,
        "dashboard_may_render_only": True,
    }


def runtime_behavior_manifest(client: TestClient) -> dict[str, Any]:
    runtime = client.get("/runtime/status").json()
    proof = client.get("/api/system/dependency-chain-proof").json()
    reconciliation = client.get("/api/system/endpoint-reconciliation").json()
    standards = client.get("/api/system/standards-control-map").json()
    design_status = client.get("/design-portal/status").json()
    cad_intent = client.get("/cad/intent").json()
    cad_export = client.get("/cad/export-contract").json()
    return {
        "schema_version": "claire.v1.runtime_behavior_manifest.v1",
        "status": "frozen_ready",
        "runtime_status": runtime.get("status"),
        "dependency_proof_status": proof.get("status"),
        "endpoint_reconciliation_status": reconciliation.get("status"),
        "standards_control_status": standards.get("status"),
        "design_portal_status": design_status.get("status"),
        "cad_intent_status": cad_intent.get("status"),
        "cad_export_contract_status": cad_export.get("status"),
        "route_count": proof.get("mounted_route_count"),
        "blocked_runtime_behaviors": {
            "runtime_truth_mutation": True,
            "automatic_update_apply_without_owner_gate": True,
            "cad_export_implementation": True,
            "autonomous_live_web_execution": True,
        },
        "proof_boundaries": proof.get("boundaries", {}),
    }


def export_manifests(output_dir: Path) -> dict[str, str]:
    app = create_app()
    client = TestClient(app)
    payloads = {
        "active_endpoints": active_endpoints(app),
        "route_contract_test_gate_map": route_contract_test_gate_map(),
        "standards_control_map": build_standards_control_map(app),
        "cad_export_contract": client.get("/cad/export-contract").json(),
        "dashboard_backend_route_manifest": dashboard_backend_route_manifest(client),
        "runtime_behavior_manifest": runtime_behavior_manifest(client),
    }
    paths: dict[str, str] = {}
    for name, payload in payloads.items():
        path = output_dir / f"v1_0_{name}_20260524.json"
        write_json(path, payload)
        paths[name] = str(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()
    print(json.dumps(export_manifests(Path(args.output_dir)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
