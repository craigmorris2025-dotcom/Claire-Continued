from __future__ import annotations

import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path.cwd()
REPORTS = ROOT / "reports"
DATA = ROOT / "data"
EXPORTS = ROOT / "exports" / "governed_outputs"

REQUIRED_IMPORTS = [
    "claire",
    "claire.api.governed_discovery_candidates",
    "claire.api.governed_useful_outputs",
    "claire.api.governed_review_queue",
    "claire.api.governed_reviewed_exports",
    "claire.api.governed_route_repeat",
    "claire.api.governed_demo_run",
    "claire.api.governed_s85_s91_payload",
    "claire.api.governed_s92_s98_cockpit_contracts",
    "claire.api.governed_s99_s105_routes",
]

REQUIRED_FILES = [
    "claire/api/governed_discovery_candidates.py",
    "claire/api/governed_useful_outputs.py",
    "claire/api/governed_review_queue.py",
    "claire/api/governed_reviewed_exports.py",
    "claire/api/governed_route_repeat.py",
    "claire/api/governed_demo_run.py",
    "claire/api/governed_s85_s91_payload.py",
    "claire/api/governed_s92_s98_cockpit_contracts.py",
    "claire/api/governed_s99_s105_routes.py",
]

REQUIRED_OPERATOR_ROUTES = [
    "/api/governed/operator/proof-panel",
    "/api/governed/operator/review-queue",
    "/api/governed/operator/review-action",
    "/api/governed/operator/route-demo",
    "/api/governed/operator/export-manifest",
    "/api/governed/operator/cockpit-card",
    "/api/governed/operator/fetch-map",
    "/api/governed/operator/swagger-proof",
    "/api/governed/operator/api-demo-proof",
]

REQUIRED_LOCKS = [
    "backend_owns_truth",
    "cockpit_presentation_only",
    "runtime_truth_mutation_blocked",
    "runtime_truth_write_blocked",
    "automatic_updates_blocked",
    "autonomous_execution_blocked",
    "manual_promotion_mandatory",
    "quarantine_mandatory",
]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def verify_files() -> Dict[str, Any]:
    files = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        files.append({"path": rel, "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0})
    return {"ok": all(item["exists"] and item["size_bytes"] > 0 for item in files), "required_count": len(files), "files": files}

def verify_imports() -> Dict[str, Any]:
    results = []
    for module_name in REQUIRED_IMPORTS:
        try:
            module = importlib.import_module(module_name)
            results.append({"module": module_name, "ok": True, "file": str(getattr(module, "__file__", ""))})
        except Exception as exc:
            results.append({"module": module_name, "ok": False, "error": repr(exc)})
    return {"ok": all(item["ok"] for item in results), "required_count": len(results), "imports": results}

def verify_existing_app_can_import() -> Dict[str, Any]:
    candidates = ["claire.app", "main"]
    results = []
    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
            results.append({
                "module": module_name,
                "ok": True,
                "has_create_app": hasattr(module, "create_app"),
                "has_app": hasattr(module, "app"),
                "file": str(getattr(module, "__file__", "")),
            })
        except Exception as exc:
            results.append({"module": module_name, "ok": False, "error": repr(exc)})
    return {"ok": any(item.get("ok") for item in results), "results": results}

def verify_fastapi_routes() -> Dict[str, Any]:
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from claire.api.governed_s99_s105_routes import include_governed_s99_s105_routes
    except Exception as exc:
        return {"ok": False, "error": repr(exc), "routes": []}

    app = FastAPI()
    include_governed_s99_s105_routes(app)
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    if openapi.status_code != 200:
        return {"ok": False, "error": f"openapi returned {openapi.status_code}", "routes": []}

    paths = sorted(openapi.json().get("paths", {}).keys())
    route_results = [{"route": route, "mounted": route in paths} for route in REQUIRED_OPERATOR_ROUTES]
    endpoint_checks = {}
    for route in [
        "/api/governed/operator/proof-panel",
        "/api/governed/operator/review-queue",
        "/api/governed/operator/export-manifest",
        "/api/governed/operator/cockpit-card",
        "/api/governed/operator/fetch-map",
        "/api/governed/operator/swagger-proof",
        "/api/governed/operator/api-demo-proof",
    ]:
        response = client.get(route)
        endpoint_checks[route] = {"status_code": response.status_code, "ok": response.status_code == 200}

    return {
        "ok": all(item["mounted"] for item in route_results) and all(item["ok"] for item in endpoint_checks.values()),
        "mounted_route_count": len(paths),
        "required_operator_route_count": len(REQUIRED_OPERATOR_ROUTES),
        "routes": route_results,
        "endpoint_checks": endpoint_checks,
    }

def verify_demo_contracts() -> Dict[str, Any]:
    try:
        from claire.api.governed_s92_s98_cockpit_contracts import (
            build_end_to_end_cockpit_demo_proof,
            build_review_queue_status,
            build_export_manifest,
        )
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}

    evidence = {
        "basket_id": "s105_check_basket",
        "trust_score": 0.82,
        "evidence_items": [{"evidence_id": "s105_ev_001", "title": "S105 system check evidence", "trust_score": 0.82}],
    }
    extraction = {
        "extraction_id": "s105_check_extraction",
        "signals": [
            {"label": "operator readiness signal", "type": "portfolio", "confidence": 0.8},
            {"label": "dashboard control signal", "type": "design", "confidence": 0.72},
        ],
    }
    DATA.mkdir(parents=True, exist_ok=True)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    store_path = DATA / "s105_check_review_queue.json"
    export_dir = EXPORTS / "s105_check"

    proof = build_end_to_end_cockpit_demo_proof(evidence, extraction, store_path=store_path, export_dir=export_dir)
    queue = build_review_queue_status(store_path=store_path)
    manifest = build_export_manifest(export_dir=export_dir)

    return {
        "ok": proof.get("status") == "ready" and manifest.get("export_count", 0) >= 1,
        "proof_status": proof.get("status"),
        "review_queue_total": queue.get("total_items"),
        "export_count": manifest.get("export_count"),
        "review_store_exists": store_path.exists(),
        "export_dir_exists": export_dir.exists(),
        "authority": proof.get("locks", {}),
    }

def verify_governance_locks() -> Dict[str, Any]:
    try:
        from claire.api.governed_s92_s98_cockpit_contracts import LOCKS as cockpit_locks
        from claire.api.governed_s99_s105_routes import LOCKS as route_locks
    except Exception as exc:
        return {"ok": False, "error": repr(exc), "locks": {}}

    combined = dict(cockpit_locks)
    combined.update(route_locks)
    checks = {key: combined.get(key) is True for key in REQUIRED_LOCKS}
    dangerous_flags = {
        "runtime_truth_write_enabled": combined.get("runtime_truth_write_enabled") is True,
        "runtime_truth_mutation_enabled": combined.get("runtime_truth_mutation_enabled") is True,
        "automatic_updates_enabled": combined.get("automatic_updates_enabled") is True,
        "autonomous_execution_enabled": combined.get("autonomous_execution_enabled") is True,
    }
    return {"ok": all(checks.values()) and not any(dangerous_flags.values()), "required_locks": checks, "dangerous_flags": dangerous_flags, "locks": combined}

def build_report() -> Dict[str, Any]:
    sections = {
        "files": verify_files(),
        "imports": verify_imports(),
        "existing_app_import": verify_existing_app_can_import(),
        "fastapi_operator_routes": verify_fastapi_routes(),
        "demo_contracts": verify_demo_contracts(),
        "governance_locks": verify_governance_locks(),
    }
    critical = ["files", "imports", "fastapi_operator_routes", "demo_contracts", "governance_locks"]
    ok = all(sections[key].get("ok") is True for key in critical)
    return {
        "report_version": "v19.89.8-S105-CHECK",
        "generated_at": _utc_now(),
        "status": "system_check_passed" if ok else "system_check_failed",
        "ok": ok,
        "stop_gate": "S105-CHECK",
        "forward_motion_allowed": ok,
        "next_allowed_phase": "S106 canonical runtime spine map" if ok else "repair failing S105-CHECK section only",
        "summary": {
            "required_files_ok": sections["files"].get("ok"),
            "imports_ok": sections["imports"].get("ok"),
            "operator_routes_ok": sections["fastapi_operator_routes"].get("ok"),
            "demo_contract_ok": sections["demo_contracts"].get("ok"),
            "governance_locks_ok": sections["governance_locks"].get("ok"),
        },
        "sections": sections,
    }

def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    report = build_report()
    out = REPORTS / "s105_system_verification_report.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"Report written: {out}")
    print(f"STOP GATE STATUS: {report['status']}")
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
