
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

VERSION = "v17.78"
CONTRACT_NAME = "Desktop Packaging + Startup Reliability"

REPORT_PATH = Path("data/desktop_packaging/startup_reliability_report.json")
PACKAGE_MANIFEST_PATH = Path("data/desktop_packaging/desktop_package_manifest.json")
CHECKLIST_PATH = Path("data/desktop_packaging/startup_reliability_checklist.md")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/desktop_startup_reliability_payload.json")
STOP_GO_PATH = Path("data/desktop_packaging/v17_78_desktop_startup_stop_go.json")
STOP_GO_MD_PATH = Path("data/desktop_packaging/v17_78_desktop_startup_stop_go.md")

CORE_STARTUP_FILES = {
    "primary_launcher": "LAUNCH_PLATFORM.bat",
    "safe_launcher": "START_CLAIRE_SAFE.bat",
    "startup_verifier": "VERIFY_CLAIRE_STARTUP.bat",
    "app": "claire/app.py",
    "dashboard": "frontend/command_center/modern/index.html",
    "dashboard_js": "frontend/command_center/modern/claire_workspace_agent_dashboard.js",
    "dashboard_css": "frontend/command_center/modern/claire_workspace_agent_dashboard.css",
    "requirements": "requirements.txt",
    "pyproject": "pyproject.toml",
    "version_json": "version.json",
}

PACKAGE_FILES = {
    "runtime_truth": "data/runtime/runtime_truth_canonical.json",
    "dashboard_state": "data/dashboard/operator_dashboard_state.json",
    "search_capabilities": "data/operator/search_command/search_command_capabilities.json",
    "platform_smoke": "data/proof/platform_endpoint_smoke_proof.json",
    "launch_hardening": "data/launch_hardening/platform_launch_hardening_report.json",
    "launch_hardening_stop_go": "data/launch_hardening/v17_77_launch_hardening_stop_go.json",
}

REQUIRED_IMPORTS = [
    "fastapi",
    "uvicorn",
    "pydantic",
]

VERIFY_URLS = [
    "http://127.0.0.1:8000/docs",
    "http://127.0.0.1:8000/operator/dashboard/state",
    "http://127.0.0.1:8000/operator/search/capabilities",
    "http://127.0.0.1:8000/platform/launch-hardening",
    "http://127.0.0.1:8000/desktop/startup",
]

STARTUP_COMMANDS = [
    "python -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q",
    "START_CLAIRE_SAFE.bat",
    "VERIFY_CLAIRE_STARTUP.bat",
]


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


def python_environment(root: Path) -> Dict[str, Any]:
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    selected = str(venv_python) if venv_python.exists() else sys.executable
    return {
        "python_executable": sys.executable,
        "selected_launcher_python": selected,
        "python_version": sys.version,
        "venv_exists": (root / ".venv").exists(),
        "venv_python_exists": venv_python.exists(),
        "working_directory": str(root),
    }


def import_check() -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for module in REQUIRED_IMPORTS:
        try:
            __import__(module)
            results[module] = {"status": "passed"}
        except Exception as exc:
            results[module] = {"status": "failed", "error": str(exc)}
    try:
        from runtime_core.app import app
        route_count = len(getattr(app, "routes", []) or [])
        results["runtime_core.app"] = {"status": "passed", "route_count": route_count}
    except Exception as exc:
        results["runtime_core.app"] = {"status": "failed", "error": str(exc), "traceback": traceback.format_exc(limit=8)}
    return results


def file_inventory(root: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    combined = {**CORE_STARTUP_FILES, **PACKAGE_FILES}
    for name, relative in combined.items():
        path = root / relative
        out[name] = {
            "path": relative,
            "exists": path.exists(),
            "is_file": path.is_file(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        }
    return out


def port_status(host: str = "127.0.0.1", port: int = 8000) -> Dict[str, Any]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.35)
    try:
        code = sock.connect_ex((host, port))
        occupied = code == 0
        return {
            "host": host,
            "port": port,
            "occupied": occupied,
            "status": "already_running_or_occupied" if occupied else "available",
            "message": "Port 8000 is occupied. Claire may already be running." if occupied else "Port 8000 is available for startup.",
        }
    except Exception as exc:
        return {"host": host, "port": port, "occupied": None, "status": "unknown", "error": str(exc)}
    finally:
        try:
            sock.close()
        except Exception:
            pass


def launcher_content_check(root: Path) -> Dict[str, Any]:
    checks: Dict[str, Any] = {}
    for name in ["primary_launcher", "safe_launcher", "startup_verifier"]:
        relative = CORE_STARTUP_FILES[name]
        path = root / relative
        if not path.exists():
            checks[name] = {"status": "missing", "path": relative}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        checks[name] = {
            "status": "passed" if "main:app" in lower or name == "startup_verifier" else "warning",
            "path": relative,
            "starts_uvicorn_platform_app": "uvicorn main:app" in lower,
            "opens_dashboard": "frontend\\command_center\\modern\\index.html" in lower or "frontend/command_center/modern/index.html" in lower,
            "opens_swagger": "127.0.0.1:8000/docs" in lower,
            "line_count": len(text.splitlines()),
        }
    return checks


def platform_continuity(root: Path) -> Dict[str, Any]:
    launch_hardening, hardening_source = read_json(root / "data/launch_hardening/platform_launch_hardening_report.json")
    stop_go, stop_source = read_json(root / "data/launch_hardening/v17_77_launch_hardening_stop_go.json")
    smoke, smoke_source = read_json(root / "data/proof/platform_endpoint_smoke_proof.json")
    proof, proof_source = read_json(root / "data/proof/full_end_to_end_proof_pack.json")

    return {
        "launch_hardening_source": hardening_source,
        "launch_hardening_status": (launch_hardening.get("stop_go") or {}).get("status", launch_hardening.get("status", "missing")),
        "launch_hardening_stop_go_source": stop_source,
        "launch_hardening_stop_go_status": stop_go.get("status", "missing"),
        "platform_smoke_source": smoke_source,
        "platform_smoke_status": smoke.get("status", "missing"),
        "e2e_proof_source": proof_source,
        "e2e_proof_status": proof.get("status", "missing"),
    }


def package_manifest(root: Path) -> Dict[str, Any]:
    files = file_inventory(root)
    package_groups = {
        "launch": ["primary_launcher", "safe_launcher", "startup_verifier"],
        "app_runtime": ["app", "requirements", "pyproject", "version_json"],
        "frontend": ["dashboard", "dashboard_js", "dashboard_css"],
        "truth_and_proof": list(PACKAGE_FILES.keys()),
    }
    missing_by_group: Dict[str, List[str]] = {}
    for group, names in package_groups.items():
        missing_by_group[group] = [name for name in names if not files.get(name, {}).get("exists")]

    manifest = {
        "version": VERSION,
        "contract_name": "Desktop Package Manifest",
        "generated_at": now(),
        "package_root": str(root),
        "package_type": "local_desktop_source_package",
        "not_an_exe_yet": True,
        "executable_packaging_prepared_later": True,
        "groups": package_groups,
        "files": files,
        "missing_by_group": missing_by_group,
        "required_startup_commands": STARTUP_COMMANDS,
        "verify_urls": VERIFY_URLS,
        "governance": {
            "no_live_internet_enablement": True,
            "no_automatic_update_execution": True,
            "no_background_execution": True,
            "operator_review_required": True,
            "source_project_remains_editable": True,
        },
    }
    write_json(root / PACKAGE_MANIFEST_PATH, manifest)
    return manifest


def determine_stop_go(report: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    for name, item in report["imports"].items():
        if item.get("status") != "passed":
            blockers.append(f"import_failed:{name}")

    for name in CORE_STARTUP_FILES:
        item = report["files"].get(name, {})
        if not item.get("exists"):
            blockers.append(f"missing_startup_file:{name}")

    for group, missing in report["package_manifest"].get("missing_by_group", {}).items():
        if missing and group in {"launch", "app_runtime", "frontend"}:
            blockers.append(f"package_group_missing:{group}:{','.join(missing)}")
        elif missing:
            warnings.append(f"package_group_missing:{group}:{','.join(missing)}")

    primary = report["launcher_checks"].get("primary_launcher", {})
    safe = report["launcher_checks"].get("safe_launcher", {})
    if primary.get("starts_uvicorn_platform_app") is not True:
        blockers.append("primary_launcher_does_not_start_uvicorn_claire_app")
    if safe.get("starts_uvicorn_platform_app") is not True:
        blockers.append("safe_launcher_does_not_start_uvicorn_claire_app")

    continuity = report["platform_continuity"]
    if continuity.get("launch_hardening_stop_go_status") == "STOP":
        warnings.append("prior_launch_hardening_stop_go_is_STOP")
    if continuity.get("platform_smoke_status") == "STOP":
        warnings.append("prior_platform_smoke_is_STOP")

    safety = report["safety_locks"]
    if safety.get("status") != "passed":
        blockers.append("safety_locks_failed")

    if blockers:
        status = "STOP"
        recommendation = "Fix desktop startup blockers before packaging or launch-candidate freeze."
    elif warnings:
        status = "GO_WITH_WARNINGS_TO_MANUAL_STARTUP_PROOF"
        recommendation = "Desktop startup package is prepared, but warnings remain. Run manual startup proof next."
    else:
        status = "GO_TO_MANUAL_STARTUP_PROOF"
        recommendation = "Desktop startup reliability checks passed. Run manual startup and Swagger proof next."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
    }


def safety_locks(root: Path) -> Dict[str, Any]:
    internet, _ = read_json(root / "data/internet_readiness/internet_readiness_verification.json")
    runner, _ = read_json(root / "data/update_packs/automatic_update_runner_gate.json")
    search, _ = read_json(root / "data/operator/search_command/search_command_capabilities.json")

    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}
    runner_contract = runner.get("runner_contract") if isinstance(runner.get("runner_contract"), dict) else {}
    live_web = search.get("live_web_conditions") if isinstance(search.get("live_web_conditions"), dict) else {}

    checks = {
        "live_internet_disabled": readiness.get("live_internet_enabled", False) is False,
        "automatic_updates_disabled": readiness.get("automatic_updates_enabled", False) is False,
        "runner_execution_disabled": runner_contract.get("execution_enabled", False) is False,
        "runner_background_disabled": runner_contract.get("background_execution_enabled", False) is False,
        "search_live_web_disabled": live_web.get("current_live_web_enabled", False) is False,
        "search_automatic_updates_disabled": live_web.get("current_automatic_updates_enabled", False) is False,
    }
    return {"status": "passed" if all(checks.values()) else "blocked", "checks": checks}


def write_checklist(root: Path, report: Dict[str, Any]) -> None:
    lines = [
        "# Claire v17.78 Desktop Startup Reliability Checklist",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Run",
        "",
        "```bat",
        "python -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q",
        "START_CLAIRE_SAFE.bat",
        "VERIFY_CLAIRE_STARTUP.bat",
        "```",
        "",
        "## Confirm URLs",
        "",
    ]
    for url in VERIFY_URLS:
        lines.append(f"- {url}")
    lines.extend([
        "",
        "## Expected",
        "",
        "- Backend imports successfully.",
        "- Swagger opens.",
        "- Dashboard opens.",
        "- Dashboard says Backend Online after refresh.",
        "- Search capabilities endpoint responds.",
        "- Live internet remains disabled.",
        "- Automatic updates remain disabled.",
        "",
        "## Stop / Go",
        "",
        f"Status: **{report['stop_go']['status']}**",
        "",
        f"Recommendation: {report['stop_go']['recommendation']}",
        "",
    ])
    if report["stop_go"]["blockers"]:
        lines.append("### Blockers")
        for item in report["stop_go"]["blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    if report["stop_go"]["warnings"]:
        lines.append("### Warnings")
        for item in report["stop_go"]["warnings"]:
            lines.append(f"- {item}")
        lines.append("")
    write_text(root / CHECKLIST_PATH, "\n".join(lines))
    write_text(root / STOP_GO_MD_PATH, "\n".join([
        "# Claire v17.78 Desktop Startup Stop / Go",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"Status: **{report['stop_go']['status']}**",
        "",
        f"Recommendation: {report['stop_go']['recommendation']}",
        "",
        "See `data/desktop_packaging/startup_reliability_checklist.md` for manual startup steps.",
    ]))


def build_desktop_startup_reliability(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    manifest = package_manifest(root)

    report = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "environment": python_environment(root),
        "imports": import_check(),
        "files": file_inventory(root),
        "port": port_status(),
        "launcher_checks": launcher_content_check(root),
        "platform_continuity": platform_continuity(root),
        "package_manifest": manifest,
        "safety_locks": safety_locks(root),
        "startup_commands": STARTUP_COMMANDS,
        "verify_urls": VERIFY_URLS,
        "governance": {
            "desktop_startup_reliability_only": True,
            "source_package_not_exe": True,
            "live_internet_disabled": True,
            "automatic_updates_disabled": True,
            "background_execution_disabled": True,
            "operator_review_required": True,
            "manual_startup_proof_required": True,
            "manual_swagger_proof_required": True,
        },
        "next": [
            "v17.79 Manual Browser + Swagger Proof Binder",
            "v17.80 Launch Candidate Freeze",
            "v17.81 Cleanup Proof Before Archive/Delete",
        ],
    }

    report["stop_go"] = determine_stop_go(report)

    write_json(root / REPORT_PATH, report)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": report["generated_at"], **report["stop_go"]})
    write_checklist(root, report)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": report["generated_at"],
        "status": report["stop_go"]["status"],
        "recommendation": report["stop_go"]["recommendation"],
        "blockers": report["stop_go"]["blockers"],
        "warnings": report["stop_go"]["warnings"],
        "environment": report["environment"],
        "port": report["port"],
        "launcher_checks": report["launcher_checks"],
        "verify_urls": VERIFY_URLS,
        "safety_locks": report["safety_locks"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return report


def desktop_startup_reliability_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    report = build_desktop_startup_reliability(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": report.get("stop_go", {}).get("status"),
        "recommendation": report.get("stop_go", {}).get("recommendation"),
        "blockers": report.get("stop_go", {}).get("blockers", []),
        "warnings": report.get("stop_go", {}).get("warnings", []),
        "verify_urls": report.get("verify_urls", []),
        "startup_commands": report.get("startup_commands", []),
    }
