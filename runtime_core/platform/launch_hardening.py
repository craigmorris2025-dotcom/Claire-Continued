
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.77"
CONTRACT_NAME = "Platform Launch Hardening"

REPORT_PATH = Path("data/launch_hardening/platform_launch_hardening_report.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/platform_launch_hardening_payload.json")
STOP_GO_PATH = Path("data/launch_hardening/v17_77_launch_hardening_stop_go.json")
STOP_GO_MD_PATH = Path("data/launch_hardening/v17_77_launch_hardening_stop_go.md")

REQUIRED_FILES = {
    "app": "claire/app.py",
    "launcher": "LAUNCH_PLATFORM.bat",
    "dashboard": "frontend/command_center/modern/index.html",
    "dashboard_js": "frontend/command_center/modern/claire_workspace_agent_dashboard.js",
    "dashboard_css": "frontend/command_center/modern/claire_workspace_agent_dashboard.css",
    "operator_dashboard_route": "claire/api/routes_operator_dashboard.py",
    "operator_search_route": "claire/api/routes_operator_search_command.py",
    "platform_smoke_route": "claire/api/routes_platform_endpoint_smoke_proof.py",
    "operator_dashboard_state": "claire/dashboard/operator_dashboard_state.py",
    "search_command_layer": "claire/operator/search_command_layer.py",
    "runtime_truth": "data/runtime/runtime_truth_canonical.json",
    "platform_smoke_proof": "data/proof/platform_endpoint_smoke_proof.json",
    "platform_stop_go": "data/proof/v17_76_platform_stop_go_report.json",
}

REQUIRED_IMPORTS = [
    "fastapi",
    "uvicorn",
    "pydantic",
]

REQUIRED_ENDPOINTS = [
    "/operator/dashboard/state",
    "/operator/search/capabilities",
    "/runtime/truth",
    "/routes/audit",
    "/autodesign/handoff",
    "/design-portal/output",
    "/validation/buildability",
    "/internet/readiness",
    "/updates/regression-lock",
    "/proof/e2e",
    "/proof/platform-smoke",
]

FORBIDDEN_LAUNCHER_PATTERNS = [
    "python main.py",
    "cd src",
    "src\\main.py",
    "backend.app",
    "backend.main",
]

REQUIRED_LAUNCHER_PATTERNS = [
    "uvicorn main:app",
    "127.0.0.1",
    "8000",
    "frontend\\command_center\\modern\\index.html",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def file_inventory(root: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, relative in REQUIRED_FILES.items():
        path = root / relative
        out[name] = {
            "path": relative,
            "exists": path.exists(),
            "is_file": path.is_file(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        }
    return out


def import_check() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for module in REQUIRED_IMPORTS:
        try:
            __import__(module)
            results[module] = {"status": "passed"}
        except Exception as exc:
            results[module] = {"status": "failed", "error": str(exc)}
    try:
        from runtime_core.app import app  # noqa: F401
        results["runtime_core.app"] = {"status": "passed"}
    except Exception as exc:
        results["runtime_core.app"] = {"status": "failed", "error": str(exc), "traceback": traceback.format_exc(limit=8)}
    return results


def port_check(host: str = "127.0.0.1", port: int = 8000) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.35)
    try:
        result = sock.connect_ex((host, port))
        occupied = result == 0
        return {
            "host": host,
            "port": port,
            "occupied": occupied,
            "status": "warning_occupied" if occupied else "available",
            "message": "Port is already in use; that may mean Claire is already running." if occupied else "Port is available for launch.",
        }
    except Exception as exc:
        return {"host": host, "port": port, "occupied": None, "status": "unknown", "error": str(exc)}
    finally:
        try:
            sock.close()
        except Exception:
            pass


def launcher_check(root: Path) -> Dict[str, Any]:
    launcher = root / "LAUNCH_PLATFORM.bat"
    if not launcher.exists():
        return {"status": "failed", "errors": ["LAUNCH_PLATFORM.bat missing"], "warnings": []}
    text = launcher.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()

    errors = []
    warnings = []
    for pattern in REQUIRED_LAUNCHER_PATTERNS:
        if pattern.lower() not in lower:
            errors.append(f"launcher_missing_required_pattern:{pattern}")
    for pattern in FORBIDDEN_LAUNCHER_PATTERNS:
        if pattern.lower() in lower:
            warnings.append(f"launcher_contains_legacy_pattern:{pattern}")

    return {
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "line_count": len(text.splitlines()),
    }


def route_registration_check(root: Path) -> Dict[str, Any]:
    app_path = root / "claire/app.py"
    if not app_path.exists():
        return {"status": "failed", "errors": ["claire/app.py missing"], "registered": []}
    text = app_path.read_text(encoding="utf-8", errors="replace")
    expected_modules = [
        "routes_operator_dashboard",
        "routes_operator_search_command",
        "routes_runtime_truth",
        "routes_route_audit",
        "routes_autodesign_handoff",
        "routes_design_portal_output",
        "routes_buildability_validation",
        "routes_internet_readiness",
        "routes_update_pack_staging",
        "routes_rollback_update_plan",
        "routes_automatic_update_runner_gate",
        "routes_update_governance_regression_lock",
        "routes_full_e2e_proof_pack",
        "routes_platform_endpoint_smoke_proof",
    ]
    registered = [name for name in expected_modules if name in text]
    missing = [name for name in expected_modules if name not in text]
    return {
        "status": "passed" if not missing else "warning",
        "registered": registered,
        "missing": missing,
        "registered_count": len(registered),
        "expected_count": len(expected_modules),
    }


def endpoint_presence_check() -> Dict[str, Any]:
    try:
        from runtime_core.app import app
    except Exception as exc:
        return {"status": "failed", "error": str(exc), "endpoints": []}

    endpoints = []
    try:
        routes = getattr(app, "routes", [])
        for route in routes:
            path = getattr(route, "path", "")
            methods = sorted(list(getattr(route, "methods", []) or []))
            endpoints.append({"path": path, "methods": methods})
    except Exception as exc:
        return {"status": "failed", "error": str(exc), "endpoints": []}

    paths = {item["path"] for item in endpoints}
    missing = [path for path in REQUIRED_ENDPOINTS if path not in paths]
    return {
        "status": "passed" if not missing else "warning",
        "required_missing": missing,
        "required_present": [path for path in REQUIRED_ENDPOINTS if path in paths],
        "endpoint_count": len(endpoints),
        "endpoints": endpoints[:300],
    }


def platform_smoke_status(root: Path) -> Dict[str, Any]:
    smoke, source = read_json(root / "data/proof/platform_endpoint_smoke_proof.json")
    stop_go, stop_go_source = read_json(root / "data/proof/v17_76_platform_stop_go_report.json")
    return {
        "source": source,
        "stop_go_source": stop_go_source,
        "proof_status": smoke.get("status", "missing"),
        "stop_go_status": stop_go.get("status", smoke.get("status", "missing")),
        "recommendation": stop_go.get("recommendation", ""),
        "domain_status": {name: item.get("status") for name, item in (smoke.get("domains") if isinstance(smoke.get("domains"), dict) else {}).items() if isinstance(item, dict)},
    }


def safety_lock_check(root: Path) -> Dict[str, Any]:
    internet, _ = read_json(root / "data/internet_readiness/internet_readiness_verification.json")
    runner, _ = read_json(root / "data/update_packs/automatic_update_runner_gate.json")
    lock, _ = read_json(root / "data/update_packs/update_governance_regression_lock.json")
    search, _ = read_json(root / "data/operator/search_command/search_command_capabilities.json")

    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}
    runner_contract = runner.get("runner_contract") if isinstance(runner.get("runner_contract"), dict) else {}
    lock_state = lock.get("lock_state") if isinstance(lock.get("lock_state"), dict) else {}
    live_web = search.get("live_web_conditions") if isinstance(search.get("live_web_conditions"), dict) else {}

    checks = {
        "live_internet_disabled": readiness.get("live_internet_enabled", False) is False,
        "automatic_updates_disabled": readiness.get("automatic_updates_enabled", False) is False,
        "runner_execution_disabled": runner_contract.get("execution_enabled", False) is False,
        "runner_background_disabled": runner_contract.get("background_execution_enabled", False) is False,
        "regression_lock_active": lock_state.get("regression_lock_active", False) is True,
        "search_live_web_disabled": live_web.get("current_live_web_enabled", False) is False,
        "search_auto_updates_disabled": live_web.get("current_automatic_updates_enabled", False) is False,
    }
    return {
        "status": "passed" if all(checks.values()) else "blocked",
        "checks": checks,
    }


def create_runtime_launcher(root: Path) -> Dict[str, Any]:
    launcher_text = """@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===============================================
echo  Claire Syntalion v17.77 Platform Launch
echo ===============================================
echo.
echo Preflight:
echo  - Backend: http://127.0.0.1:8000
echo  - Swagger: http://127.0.0.1:8000/docs
echo  - Dashboard: frontend\\command_center\\modern\\index.html
echo.

set PYTHON_EXE=python
if exist ".venv\\Scripts\\python.exe" set PYTHON_EXE=.venv\\Scripts\\python.exe

%PYTHON_EXE% -c "import runtime_core.app; print('Runtime core app import: OK')" || (
    echo.
    echo Runtime core app import failed. Run the v17.77 tests and inspect the error.
    pause
    exit /b 1
)

echo.
echo Starting Claire backend...
start "Platform Backend v17.77" cmd /k "%PYTHON_EXE% -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 6 /nobreak > nul

echo Opening Swagger and dashboard...
start "" "http://127.0.0.1:8000/docs"
start "" "%cd%\\frontend\\command_center\\modern\\index.html"

echo.
echo If the dashboard says Backend Offline, wait a few seconds and press Search/Refresh.
echo Verify: http://127.0.0.1:8000/operator/dashboard/state
echo.
endlocal
"""
    path = root / "LAUNCH_PLATFORM.bat"
    path.write_text(launcher_text, encoding="utf-8")
    return {"status": "written", "path": "LAUNCH_PLATFORM.bat"}


def determine_stop_go(report: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if report["imports"].get("runtime_core.app", {}).get("status") != "passed":
        blockers.append("runtime_core_app_import_failed")

    for name, item in report["files"].items():
        if not item.get("exists"):
            blockers.append(f"missing_required_file:{name}")

    if report["launcher"].get("status") != "passed":
        blockers.append("launcher_check_failed")
    warnings.extend(report["launcher"].get("warnings", []))

    if report["safety"].get("status") != "passed":
        blockers.append("safety_lock_failed")

    if report["endpoint_presence"].get("status") == "failed":
        blockers.append("endpoint_presence_check_failed")
    elif report["endpoint_presence"].get("required_missing"):
        warnings.append("some_expected_endpoints_not_registered:" + ",".join(report["endpoint_presence"].get("required_missing", [])))

    smoke_status = report["platform_smoke"].get("stop_go_status")
    if smoke_status == "STOP":
        warnings.append("v17_76_platform_smoke_report_is_STOP_review_before_launch")

    if blockers:
        status = "STOP"
        recommendation = "Fix launch blockers before using Claire as a platform launch candidate."
    elif warnings:
        status = "GO_WITH_WARNINGS_TO_MANUAL_BROWSER_PROOF"
        recommendation = "Launch hardening is installed, but warnings remain. Run manual browser and Swagger proof next."
    else:
        status = "GO_TO_MANUAL_BROWSER_AND_SWAGGER_PROOF"
        recommendation = "Launch hardening checks passed. Run manual browser and Swagger proof next."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
    }


def write_markdown(root: Path, report: Dict[str, Any]) -> None:
    sg = report["stop_go"]
    lines = [
        "# Claire v17.77 Platform Launch Hardening Stop / Go",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Checks",
        "",
        f"- Imports: {sum(1 for item in report['imports'].values() if item.get('status') == 'passed')}/{len(report['imports'])} passed",
        f"- Required files: {sum(1 for item in report['files'].values() if item.get('exists'))}/{len(report['files'])} present",
        f"- Launcher: {report['launcher'].get('status')}",
        f"- Route registration: {report['route_registration'].get('status')} ({report['route_registration'].get('registered_count')}/{report['route_registration'].get('expected_count')})",
        f"- Endpoint presence: {report['endpoint_presence'].get('status')}",
        f"- Safety locks: {report['safety'].get('status')}",
        f"- v17.76 platform smoke: {report['platform_smoke'].get('stop_go_status')}",
        "",
        "## Launch Commands",
        "",
        "```bat",
        "python -m pytest tests/test_v17_77_platform_launch_hardening.py -q",
        "LAUNCH_PLATFORM.bat",
        "```",
        "",
        "## Verify URLs",
        "",
        "- http://127.0.0.1:8000/docs",
        "- http://127.0.0.1:8000/operator/dashboard/state",
        "- http://127.0.0.1:8000/operator/search/capabilities",
        "- http://127.0.0.1:8000/proof/platform-smoke",
        "",
    ]
    if sg["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for blocker in sg["blockers"]:
            lines.append(f"- {blocker}")
        lines.append("")
    if sg["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for warning in sg["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def build_platform_launch_hardening(project_root: Optional[Path | str] = None, rewrite_launcher: bool = False) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    launcher_rewrite = create_runtime_launcher(root) if rewrite_launcher else {"status": "not_requested"}

    report = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "launcher_rewrite": launcher_rewrite,
        "files": file_inventory(root),
        "imports": import_check(),
        "port": port_check(),
        "launcher": launcher_check(root),
        "route_registration": route_registration_check(root),
        "endpoint_presence": endpoint_presence_check(),
        "platform_smoke": platform_smoke_status(root),
        "safety": safety_lock_check(root),
        "governance": {
            "launch_hardening_only": True,
            "live_internet_disabled": True,
            "automatic_updates_disabled": True,
            "background_execution_disabled": True,
            "operator_review_required": True,
            "manual_browser_proof_required": True,
            "swagger_proof_required": True,
        },
        "next": [
            "v17.78 Desktop Packaging / Startup Reliability",
            "v17.79 Manual Browser + Swagger Proof Binder",
            "v17.80 Launch Candidate Freeze",
        ],
    }

    report["stop_go"] = determine_stop_go(report)

    write_json(root / REPORT_PATH, report)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": report["generated_at"], **report["stop_go"]})
    write_markdown(root, report)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": report["generated_at"],
        "status": report["stop_go"]["status"],
        "recommendation": report["stop_go"]["recommendation"],
        "blockers": report["stop_go"]["blockers"],
        "warnings": report["stop_go"]["warnings"],
        "port": report["port"],
        "launcher": report["launcher"],
        "route_registration": report["route_registration"],
        "endpoint_presence": {
            "status": report["endpoint_presence"].get("status"),
            "required_present": report["endpoint_presence"].get("required_present"),
            "required_missing": report["endpoint_presence"].get("required_missing"),
        },
        "safety": report["safety"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return report


def platform_launch_hardening_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    report = build_platform_launch_hardening(project_root, rewrite_launcher=False)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": report.get("stop_go", {}).get("status"),
        "recommendation": report.get("stop_go", {}).get("recommendation"),
        "blockers": report.get("stop_go", {}).get("blockers", []),
        "warnings": report.get("stop_go", {}).get("warnings", []),
        "port": report.get("port"),
        "safety": report.get("safety"),
    }
