from __future__ import annotations

import ast
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime" / "governed_live_probe"
REPORT_PATH = RUNTIME_DIR / "s36_first_live_preflight_report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _no_body_read_in_router() -> tuple[bool, list[str]]:
    router_path = ROOT / "claire" / "api" / "routes" / "governed_live_probe.py"
    if not router_path.exists():
        return False, ["governed_live_probe.py missing"]

    source = _read(router_path)
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, [f"router syntax error: {exc}"]

    failures = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "read":
                failures.append("response/body read-style .read() call found")
    for forbidden in ["requests.get", "requests.post", "selenium", "playwright", "webdriver"]:
        if forbidden in source.lower():
            failures.append(f"forbidden token found: {forbidden}")
    return not failures, failures


def _route_visibility() -> tuple[bool, dict]:
    cmd = [sys.executable, "tools/audit_s36_route_visibility.py"]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=30)
    report_path = RUNTIME_DIR / "s36_route_visibility_audit.json"
    report = {}
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            report = {}
    ok = result.returncode == 0 and report.get("found_status_route") is True and report.get("found_head_route") is True
    report["stdout"] = result.stdout[-2000:]
    report["stderr"] = result.stderr[-2000:]
    report["returncode"] = result.returncode
    return ok, report


def _required_files() -> tuple[bool, list[str]]:
    required = [
        ROOT / "tools" / "run_s36_single_head_probe.py",
        ROOT / "tools" / "verify_s36_probe_quarantine.py",
        ROOT / "tools" / "compile_s36_first_probe_report.py",
        ROOT / "claire" / "api" / "routes" / "governed_live_probe.py",
    ]
    missing = [str(p) for p in required if not p.exists()]
    return not missing, missing


def main() -> int:
    files_ok, missing = _required_files()
    body_ok, body_failures = _no_body_read_in_router()
    route_ok, route_report = _route_visibility()

    passed = files_ok and body_ok and route_ok
    report = {
        "version": "v19.89.8-S36R15-R18-first-live-preflight",
        "checked_at": _utc_now(),
        "passed": passed,
        "required_files_present": files_ok,
        "missing_files": missing,
        "no_body_read_static_proof": body_ok,
        "body_read_failures": body_failures,
        "route_visibility_passed": route_ok,
        "route_visibility_report": route_report,
        "live_probe_executed_by_preflight": False,
        "ready_for_one_operator_head_probe": passed,
        "operator_command": "python tools/run_s36_single_head_probe.py --url https://example.com --operator-ack YES",
        "verify_command": "python tools/verify_s36_probe_quarantine.py",
        "compile_report_command": "python tools/compile_s36_first_probe_report.py",
        "invariants": {
            "metadata_only": True,
            "body_reads_allowed": False,
            "browser_execution_allowed": False,
            "runtime_truth_mutation_allowed": False,
            "autonomous_execution_allowed": False,
            "automatic_updates_allowed": False,
            "continuous_crawling_allowed": False,
            "manual_promotion_required": True,
            "quarantine_required": True,
        },
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if not passed:
        print("[S36-FIRST-LIVE-PREFLIGHT][BLOCKED]")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    print("[S36-FIRST-LIVE-PREFLIGHT] PASS")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
