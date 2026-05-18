
from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.76"
CONTRACT_NAME = "Platform Endpoint Smoke Proof + Launch Hardening Gate"

PROOF_PATH = Path("data/proof/platform_endpoint_smoke_proof.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/platform_endpoint_smoke_payload.json")
STOP_GO_PATH = Path("data/proof/v17_76_platform_stop_go_report.json")
STOP_GO_MD_PATH = Path("data/proof/v17_76_platform_stop_go_report.md")

CORE_ENDPOINTS = [
    {"name": "root", "method": "GET", "path": "/", "required": False, "domain": "core"},
    {"name": "health", "method": "GET", "path": "/health", "required": False, "domain": "core"},
    {"name": "operator_dashboard_state", "method": "GET", "path": "/operator/dashboard/state", "required": True, "domain": "dashboard"},
    {"name": "dashboard_state", "method": "GET", "path": "/dashboard/state", "required": True, "domain": "dashboard"},
    {"name": "operator_search_capabilities", "method": "GET", "path": "/operator/search/capabilities", "required": True, "domain": "search"},
    {"name": "operator_search_query", "method": "POST", "path": "/operator/search/query", "required": True, "domain": "search", "json": {"query": "runtime", "mode": "runtime", "limit": 3}},
    {"name": "operator_command_parse", "method": "POST", "path": "/operator/command/parse", "required": True, "domain": "search", "json": {"query": "open autodesign"}},
    {"name": "runtime_truth", "method": "GET", "path": "/runtime/truth", "required": True, "domain": "runtime_truth"},
    {"name": "runtime_state", "method": "GET", "path": "/runtime/state", "required": True, "domain": "runtime_truth"},
    {"name": "route_audit", "method": "GET", "path": "/routes/audit", "required": True, "domain": "routes"},
    {"name": "route_audit_summary", "method": "GET", "path": "/routes/audit/summary", "required": True, "domain": "routes"},
    {"name": "autodesign_handoff", "method": "GET", "path": "/autodesign/handoff", "required": True, "domain": "autodesign"},
    {"name": "autodesign_handoff_summary", "method": "GET", "path": "/autodesign/handoff/summary", "required": True, "domain": "autodesign"},
    {"name": "design_portal_output", "method": "GET", "path": "/design-portal/output", "required": True, "domain": "design_portal"},
    {"name": "design_portal_output_summary", "method": "GET", "path": "/design-portal/output/summary", "required": True, "domain": "design_portal"},
    {"name": "buildability_validation", "method": "GET", "path": "/validation/buildability", "required": True, "domain": "validation"},
    {"name": "buildability_validation_summary", "method": "GET", "path": "/validation/buildability/summary", "required": True, "domain": "validation"},
    {"name": "internet_readiness", "method": "GET", "path": "/internet/readiness", "required": True, "domain": "internet"},
    {"name": "internet_readiness_summary", "method": "GET", "path": "/internet/readiness/summary", "required": True, "domain": "internet"},
    {"name": "update_staging", "method": "GET", "path": "/updates/staging", "required": True, "domain": "updates"},
    {"name": "rollback_plan", "method": "GET", "path": "/updates/rollback-plan", "required": True, "domain": "updates"},
    {"name": "runner_gate", "method": "GET", "path": "/updates/runner-gate", "required": True, "domain": "updates"},
    {"name": "regression_lock", "method": "GET", "path": "/updates/regression-lock", "required": True, "domain": "updates"},
    {"name": "proof_e2e", "method": "GET", "path": "/proof/e2e", "required": True, "domain": "proof"},
    {"name": "proof_e2e_summary", "method": "GET", "path": "/proof/e2e/summary", "required": True, "domain": "proof"},
    {"name": "system_stop_go", "method": "GET", "path": "/system/stop-go", "required": True, "domain": "proof"},
]

OUTPUT_FILES = {
    "dashboard_state": "data/dashboard/operator_dashboard_state.json",
    "search_capabilities": "data/operator/search_command/search_command_capabilities.json",
    "runtime_truth": "data/runtime/runtime_truth_canonical.json",
    "route_audit": "data/routes/discovery_breakthrough_innovation_route_audit.json",
    "autodesign_handoff": "data/autodesign/autodesign_handoff_contract.json",
    "design_portal": "data/design_portal/design_portal_output_contract.json",
    "buildability_validation": "data/validation/buildability_viability_manufacturability_validation.json",
    "internet_readiness": "data/internet_readiness/internet_readiness_verification.json",
    "update_staging": "data/update_packs/update_pack_staging_index.json",
    "rollback_plan": "data/update_packs/rollback_plan_index.json",
    "runner_gate": "data/update_packs/automatic_update_runner_gate.json",
    "regression_lock": "data/update_packs/update_governance_regression_lock.json",
    "e2e_proof": "data/proof/full_end_to_end_proof_pack.json",
}

SAFETY_FLAGS = {
    "live_internet_enabled": False,
    "automatic_updates_enabled": False,
    "background_execution_enabled": False,
    "uncontrolled_web_search_enabled": False,
    "autonomous_agent_execution_enabled": False,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def output_file_inventory(root: Path) -> Dict[str, Any]:
    inventory: Dict[str, Any] = {}
    for name, rel_path in OUTPUT_FILES.items():
        path = root / rel_path
        inventory[name] = {
            "path": rel_path,
            "exists": path.exists(),
            "is_file": path.is_file(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        }
    return inventory


def load_app() -> Tuple[Optional[Any], Dict[str, Any]]:
    try:
        from claire.app import app
        return app, {"status": "loaded", "error": None}
    except Exception as exc:
        return None, {
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(limit=8),
        }


def smoke_endpoint(client: Any, endpoint: Dict[str, Any]) -> Dict[str, Any]:
    method = endpoint["method"].upper()
    path = endpoint["path"]
    try:
        if method == "GET":
            response = client.get(path)
        elif method == "POST":
            response = client.post(path, json=endpoint.get("json", {}))
        else:
            return {
                **endpoint,
                "status": "failed",
                "http_status": None,
                "error": f"Unsupported method {method}",
                "json_root_type": None,
                "body_preview": "",
            }

        body_preview = response.text[:700] if hasattr(response, "text") else ""
        json_root_type = None
        json_ok = False
        keys = []
        try:
            payload = response.json()
            json_ok = True
            json_root_type = type(payload).__name__
            if isinstance(payload, dict):
                keys = sorted(list(payload.keys()))[:40]
        except Exception:
            pass

        passed = 200 <= response.status_code < 300 and json_ok
        return {
            **endpoint,
            "status": "passed" if passed else "failed",
            "http_status": response.status_code,
            "json_ok": json_ok,
            "json_root_type": json_root_type,
            "keys": keys,
            "body_preview": body_preview,
            "error": None if passed else "Endpoint did not return 2xx JSON.",
        }
    except Exception as exc:
        return {
            **endpoint,
            "status": "failed",
            "http_status": None,
            "json_ok": False,
            "json_root_type": None,
            "keys": [],
            "body_preview": "",
            "error": str(exc),
        }


def run_endpoint_smoke() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    app, app_report = load_app()
    if app is None:
        return [], app_report

    try:
        from fastapi.testclient import TestClient
    except Exception as exc:
        return [], {
            "status": "failed",
            "error": "fastapi.testclient could not be imported: " + str(exc),
            "traceback": traceback.format_exc(limit=8),
        }

    try:
        client = TestClient(app)
        results = [smoke_endpoint(client, endpoint) for endpoint in CORE_ENDPOINTS]
        return results, app_report
    except Exception as exc:
        return [], {
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(limit=8),
        }


def domain_rollup(endpoint_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    domains: Dict[str, Any] = {}
    for endpoint in CORE_ENDPOINTS:
        domain = endpoint["domain"]
        domains.setdefault(domain, {"required": 0, "passed": 0, "failed": 0, "optional_failed": 0, "endpoints": []})

    by_path = {(item.get("method"), item.get("path")): item for item in endpoint_results}
    for endpoint in CORE_ENDPOINTS:
        domain = endpoint["domain"]
        result = by_path.get((endpoint["method"], endpoint["path"]))
        if result is None:
            status = "failed"
            result = {**endpoint, "status": "failed", "error": "not tested"}
        else:
            status = result.get("status")
        if endpoint.get("required"):
            domains[domain]["required"] += 1
            if status == "passed":
                domains[domain]["passed"] += 1
            else:
                domains[domain]["failed"] += 1
        else:
            if status != "passed":
                domains[domain]["optional_failed"] += 1
        domains[domain]["endpoints"].append(result)

    for domain, data in domains.items():
        if data["failed"]:
            data["status"] = "blocked"
        elif data["optional_failed"]:
            data["status"] = "warning"
        else:
            data["status"] = "passed"
    return domains


def inspect_safety(root: Path) -> Dict[str, Any]:
    internet, _ = read_json(root / "data/internet_readiness/internet_readiness_verification.json")
    runner, _ = read_json(root / "data/update_packs/automatic_update_runner_gate.json")
    lock, _ = read_json(root / "data/update_packs/update_governance_regression_lock.json")
    search_caps, _ = read_json(root / "data/operator/search_command/search_command_capabilities.json")

    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}
    runner_contract = runner.get("runner_contract") if isinstance(runner.get("runner_contract"), dict) else {}
    lock_state = lock.get("lock_state") if isinstance(lock.get("lock_state"), dict) else {}
    search_live = search_caps.get("live_web_conditions") if isinstance(search_caps.get("live_web_conditions"), dict) else {}

    checks = {
        "live_internet_enabled_false": readiness.get("live_internet_enabled", False) is False,
        "automatic_updates_enabled_false": readiness.get("automatic_updates_enabled", False) is False,
        "runner_executes_updates_false": runner_contract.get("runner_executes_updates", False) is False,
        "runner_background_execution_false": runner_contract.get("background_execution_enabled", False) is False,
        "regression_lock_active": lock_state.get("regression_lock_active", False) is True,
        "search_current_live_web_disabled": search_live.get("current_live_web_enabled", False) is False,
        "search_current_automatic_updates_disabled": search_live.get("current_automatic_updates_enabled", False) is False,
    }
    return {
        "status": "passed" if all(checks.values()) else "blocked",
        "checks": checks,
        "expected_flags": SAFETY_FLAGS,
    }


def determine_stop_go(domains: Dict[str, Any], files: Dict[str, Any], safety: Dict[str, Any], app_report: Dict[str, Any]) -> Dict[str, Any]:
    blocked_domains = [name for name, item in domains.items() if item.get("status") == "blocked"]
    missing_files = [name for name, item in files.items() if not item.get("exists")]
    blockers: List[str] = []

    if app_report.get("status") != "loaded":
        blockers.append("app_import_failed")
    if blocked_domains:
        blockers.extend([f"domain_blocked:{name}" for name in blocked_domains])
    if missing_files:
        blockers.extend([f"missing_output_file:{name}" for name in missing_files])
    if safety.get("status") != "passed":
        blockers.append("safety_lock_failed")

    if blockers:
        status = "STOP"
        recommendation = "Do not proceed to launch hardening until blocked endpoint, output, or safety domains are fixed."
    else:
        status = "GO_TO_PLATFORM_LAUNCH_HARDENING"
        recommendation = "Platform endpoint smoke proof passed. Continue to launch hardening, packaging, and manual browser/Swagger proof."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "blocked_domains": blocked_domains,
        "missing_files": missing_files,
        "recommendation": recommendation,
    }


def write_markdown(root: Path, proof: Dict[str, Any]) -> None:
    sg = proof["stop_go"]
    lines = [
        "# Claire v17.76 Platform Stop / Go Report",
        "",
        f"Generated: {proof['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Endpoint Domains",
        "",
    ]
    for name, item in proof["domains"].items():
        lines.append(f"- **{name}**: {item.get('status')} ({item.get('passed')}/{item.get('required')} required endpoints passed)")
    lines.extend([
        "",
        "## Safety",
        "",
        f"- Safety status: **{proof['safety']['status']}**",
        "- Live internet remains disabled unless explicitly governed later.",
        "- Automatic updates remain disabled.",
        "- Background execution remains disabled.",
        "",
    ])
    if sg["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for blocker in sg["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def build_platform_endpoint_smoke_proof(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    endpoint_results, app_report = run_endpoint_smoke()
    domains = domain_rollup(endpoint_results)
    files = output_file_inventory(root)
    safety = inspect_safety(root)
    stop_go = determine_stop_go(domains, files, safety, app_report)

    proof = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "app_import": app_report,
        "endpoint_results": endpoint_results,
        "domains": domains,
        "output_files": files,
        "safety": safety,
        "stop_go": stop_go,
        "launch_hardening_readiness": {
            "ready_for_launch_hardening": stop_go["status"] == "GO_TO_PLATFORM_LAUNCH_HARDENING",
            "ready_for_live_internet": False,
            "ready_for_automatic_updates": False,
            "requires_manual_browser_proof": True,
            "requires_swagger_proof": True,
            "requires_packaging_after_smoke_pass": True,
        },
        "governance": {
            "no_fake_endpoint_pass": True,
            "testclient_smoke_proof": True,
            "missing_outputs_remain_visible": True,
            "live_internet_disabled": True,
            "automatic_updates_disabled": True,
            "operator_review_required": True,
        },
        "next": [
            "v17.77 Platform Launch Hardening",
            "v17.78 Desktop Packaging / Startup Reliability",
            "v17.79 Manual Browser + Swagger Proof Binder",
        ],
    }

    write_json(root / PROOF_PATH, proof)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": proof["generated_at"], **stop_go})
    write_markdown(root, proof)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": proof["generated_at"],
        "status": proof["status"],
        "domain_status": {name: item.get("status") for name, item in domains.items()},
        "stop_go": stop_go,
        "safety": safety,
        "launch_hardening_readiness": proof["launch_hardening_readiness"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)
    return proof


def platform_endpoint_smoke_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    proof = build_platform_endpoint_smoke_proof(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": proof.get("status"),
        "stop_go": proof.get("stop_go"),
        "domain_status": {name: item.get("status") for name, item in proof.get("domains", {}).items()},
        "launch_hardening_readiness": proof.get("launch_hardening_readiness"),
    }
