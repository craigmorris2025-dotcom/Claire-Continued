from __future__ import annotations

import ast
import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_VERSION = "v19.89.8-S1153-S1180-system-plateau-audit"


TRUE_VALUES = {"1", "true", "yes", "on", "enabled", "allow", "allowed"}


REQUIRED_DIRS = [
    "runtime_core",
    "runtime_core/api",
    "frontend",
    "frontend/command_center/modern",
    "tests",
]

EXPECTED_GET_ROUTES = [
    "/",
    "/health",
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/dashboard/actions/registry",
    "/dashboard/actions/summary",
    "/dashboard/actions/preview/plan_search",
    "/dashboard/operator-console/contract",
    "/dashboard/operator-console/summary",
    "/dashboard/operator-console/actions",
    "/dashboard/operator-console/preview/plan_search",
    "/dashboard/operator-action/result/plan_search",
    "/dashboard/actions/result/plan_search",
    "/dashboard/visibility/summary",
    "/dashboard/status/harmonized",
    "/api/dashboard/visibility/summary",
    "/api/dashboard/status/harmonized",
    "/api/governed/live-probe/status",
]

EXPECTED_POST_ROUTES = [
    "/api/governed/live-probe/head",
]

EXPECTED_FRONTEND_ASSETS = [
    "frontend/command_center/modern/index.html",
    "frontend/command_center/modern/platform_dashboard.html",
    "frontend/command_center/modern/platform_dashboard.js",
    "frontend/command_center/modern/platform_dashboard.css",
    "frontend/command_center/modern/dashboard_operator_console_contract.js",
    "frontend/command_center/modern/dashboard_operator_console_contract.css",
]

DANGEROUS_ENV_TOGGLES = [
    "PLATFORM_ALLOW_RESPONSE_BODY_READ",
    "PLATFORM_ALLOW_BODY_READ",
    "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION",
    "PLATFORM_ALLOW_AUTONOMOUS_CRAWLING",
    "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION",
    "PLATFORM_ALLOW_RUNTIME_MUTATION",
    "PLATFORM_ALLOW_PACKAGE_INSTALL",
    "PLATFORM_ALLOW_COMMAND_EXECUTION",
    "PLATFORM_ALLOW_BROWSER_EXECUTION",
    "PLATFORM_ALLOW_AUTOMATIC_UPDATES",
]

NETWORK_ENABLE_TOGGLES = [
    "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE",
    "PLATFORM_ALLOW_HEAD_ONLY_PROBE",
    "PLATFORM_ALLOW_REAL_SEARCH_PROVIDER",
    "PLATFORM_ALLOW_CONTROLLED_HEAD_PROBE",
    "PLATFORM_ALLOW_CONTROLLED_METADATA_GET",
    "PLATFORM_ALLOW_CONTROLLED_LIMITED_BODY_GET",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except Exception:
            return ""
    except Exception:
        return ""


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _record_issue(report: dict[str, Any], severity: str, code: str, message: str, detail: Any = None) -> None:
    entry = {
        "severity": severity,
        "code": code,
        "message": message,
    }
    if detail is not None:
        entry["detail"] = _jsonable(detail)
    report.setdefault("issues", []).append(entry)


def _audit_paths(root: Path, report: dict[str, Any]) -> None:
    path_report: dict[str, Any] = {
        "required_dirs": {},
        "frontend_assets": {},
        "active_tree_policy": {
            "uses_top_level_runtime_core": (root / "runtime_core").exists(),
            "uses_top_level_frontend": (root / "frontend").exists(),
            "active_src_tree_expected": False,
            "src_exists": (root / "src").exists(),
        },
    }

    for rel in REQUIRED_DIRS:
        exists = (root / rel).exists()
        path_report["required_dirs"][rel] = exists
        if not exists:
            _record_issue(report, "blocker", "missing_required_directory", f"Missing required directory: {rel}")

    for rel in EXPECTED_FRONTEND_ASSETS:
        exists = (root / rel).exists()
        path_report["frontend_assets"][rel] = exists
        if not exists:
            _record_issue(report, "warning", "missing_frontend_asset", f"Missing expected frontend asset: {rel}")

    if (root / "src").exists():
        _record_issue(
            report,
            "warning",
            "legacy_src_tree_present",
            "A src/ tree exists even though current active tree should be top-level runtime_core/, frontend/, tests/. Review for shadow imports before future builds.",
        )

    report["paths"] = path_report


def _audit_python_syntax(root: Path, report: dict[str, Any]) -> None:
    compile_roots = [root / "runtime_core", root / "tests"]
    optional_roots = [root / "tools", root / "scripts"]
    files: list[Path] = []
    skipped: list[str] = []

    for base in compile_roots + [p for p in optional_roots if p.exists()]:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = _rel(root, path)
            if any(part in rel for part in ["backups/", "archive/", "__pycache__/", ".pytest_cache/"]):
                skipped.append(rel)
                continue
            files.append(path)

    failures: list[dict[str, Any]] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            ast.parse(source)
        except Exception as exc:
            failures.append(
                {
                    "file": _rel(root, path),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    if failures:
        _record_issue(report, "blocker", "python_syntax_failures", "One or more active Python files fail syntax/compile checks.", failures)

    report["python_syntax"] = {
        "checked_files": len(files),
        "skipped_files": len(skipped),
        "failures": failures,
    }


def _audit_environment(report: dict[str, Any]) -> None:
    dangerous = {name: os.environ.get(name) for name in DANGEROUS_ENV_TOGGLES if _is_truthy(os.environ.get(name))}
    network = {name: os.environ.get(name) for name in NETWORK_ENABLE_TOGGLES if _is_truthy(os.environ.get(name))}

    for name, value in dangerous.items():
        _record_issue(
            report,
            "blocker",
            "unsafe_authority_env_enabled",
            f"Unsafe authority environment toggle is enabled: {name}",
            value,
        )

    if network:
        _record_issue(
            report,
            "warning",
            "network_probe_env_enabled",
            "One or more controlled network/probe toggles are enabled. This may be expected only during an explicit one-shot operator probe.",
            network,
        )

    report["environment"] = {
        "dangerous_enabled": dangerous,
        "network_probe_enabled": network,
    }


def _build_test_client(report: dict[str, Any]):
    try:
        from runtime_core.app import create_app
        from fastapi.testclient import TestClient

        app = create_app()
        client = TestClient(app)
        return app, client
    except Exception:
        _record_issue(
            report,
            "blocker",
            "create_app_failed",
            "Could not import runtime_core.app.create_app() or create TestClient.",
            traceback.format_exc(),
        )
        return None, None


def _audit_routes(root: Path, report: dict[str, Any]) -> None:
    app, client = _build_test_client(report)
    if app is None or client is None:
        report["routes"] = {"available": False}
        return

    route_table = []
    for route in app.routes:
        route_table.append(
            {
                "path": getattr(route, "path", ""),
                "methods": sorted(list(getattr(route, "methods", []) or [])),
                "name": getattr(route, "name", ""),
            }
        )

    route_paths = {entry["path"] for entry in route_table}

    route_results: dict[str, Any] = {
        "available": True,
        "route_count": len(route_table),
        "route_table": route_table,
        "expected_get": {},
        "expected_post": {},
    }

    for path in EXPECTED_GET_ROUTES:
        try:
            response = client.get(path)
            route_results["expected_get"][path] = {
                "status_code": response.status_code,
                "present_in_route_table": path in route_paths,
                "sample": _safe_response_sample(response),
            }
            if response.status_code != 200:
                _record_issue(report, "blocker", "expected_get_route_not_200", f"Expected GET route did not return 200: {path}", response.status_code)
        except Exception as exc:
            route_results["expected_get"][path] = {"error": f"{type(exc).__name__}: {exc}"}
            _record_issue(report, "blocker", "expected_get_route_error", f"Expected GET route errored: {path}", route_results["expected_get"][path])

    for path in EXPECTED_POST_ROUTES:
        try:
            response = client.post(path, json={"url": "https://example.com", "operator_ack": True, "one_shot": True})
            route_results["expected_post"][path] = {
                "status_code": response.status_code,
                "present_in_route_table": path in route_paths,
                "sample": _safe_response_sample(response),
            }
            if response.status_code not in (200, 403):
                _record_issue(report, "blocker", "expected_post_route_unexpected_status", f"Expected POST route returned unexpected status: {path}", response.status_code)
        except Exception as exc:
            route_results["expected_post"][path] = {"error": f"{type(exc).__name__}: {exc}"}
            _record_issue(report, "blocker", "expected_post_route_error", f"Expected POST route errored: {path}", route_results["expected_post"][path])

    # Dashboard server logs previously showed these two 404s, so keep a direct plateau assertion.
    for legacy_path in ["/dashboard/visibility/summary", "/dashboard/status/harmonized"]:
        status = route_results["expected_get"].get(legacy_path, {}).get("status_code")
        if status != 200:
            _record_issue(
                report,
                "blocker",
                "legacy_dashboard_fetch_route_missing",
                f"Active cockpit still requests {legacy_path}, and it must return 200.",
                status,
            )

    report["routes"] = route_results


def _safe_response_sample(response: Any) -> Any:
    try:
        data = response.json()
    except Exception:
        return str(getattr(response, "text", ""))[:800]
    if isinstance(data, dict):
        return {
            "keys": sorted(data.keys())[:80],
            "status": data.get("status"),
            "ok": data.get("ok"),
            "action_count": data.get("action_count") or data.get("actions_count"),
            "unlock_allowed": data.get("unlock_allowed"),
            "execution_enabled": data.get("execution_enabled"),
            "body_read_allowed": data.get("body_read_allowed"),
            "network_request_performed": data.get("network_request_performed"),
        }
    return data


def _audit_payloads(report: dict[str, Any]) -> None:
    app, client = _build_test_client(report)
    if app is None or client is None:
        report["payload_contracts"] = {"available": False}
        return

    payload_contracts: dict[str, Any] = {}
    endpoints = [
        "/dashboard/payload",
        "/dashboard/actions/registry",
        "/dashboard/operator-console/contract",
        "/dashboard/operator-action/result/plan_search",
        "/api/governed/live-probe/status",
    ]

    for endpoint in endpoints:
        try:
            response = client.get(endpoint)
            data = response.json() if response.status_code == 200 else {}
        except Exception as exc:
            payload_contracts[endpoint] = {"error": f"{type(exc).__name__}: {exc}"}
            _record_issue(report, "blocker", "payload_endpoint_error", f"Payload endpoint errored: {endpoint}", payload_contracts[endpoint])
            continue

        payload_contracts[endpoint] = {
            "status_code": response.status_code,
            "keys": sorted(data.keys()) if isinstance(data, dict) else [],
            "status": data.get("status") if isinstance(data, dict) else None,
            "action_count": data.get("action_count") or data.get("actions_count") if isinstance(data, dict) else None,
            "unlock_allowed": data.get("unlock_allowed") if isinstance(data, dict) else None,
            "execution_enabled": data.get("execution_enabled") if isinstance(data, dict) else None,
            "body_read_allowed": data.get("body_read_allowed") if isinstance(data, dict) else None,
            "network_request_performed": data.get("network_request_performed") if isinstance(data, dict) else None,
        }

        if response.status_code != 200:
            _record_issue(report, "blocker", "payload_endpoint_not_200", f"Payload endpoint did not return 200: {endpoint}", response.status_code)
            continue

        if isinstance(data, dict):
            if endpoint in ["/dashboard/actions/registry", "/dashboard/operator-console/contract"] and int(data.get("action_count") or data.get("actions_count") or 0) < 1:
                _record_issue(report, "blocker", "action_count_zero", f"Action count is zero for {endpoint}", data)
            if data.get("unlock_allowed") is not False and endpoint != "/dashboard/payload":
                _record_issue(report, "blocker", "unlock_allowed_not_false", f"unlock_allowed must be False for {endpoint}", data.get("unlock_allowed"))
            if data.get("execution_enabled") is not False and endpoint != "/dashboard/payload":
                _record_issue(report, "blocker", "execution_enabled_not_false", f"execution_enabled must be False for {endpoint}", data.get("execution_enabled"))
            if data.get("body_read_allowed") is not False and endpoint not in ["/dashboard/payload", "/api/governed/live-probe/status"]:
                _record_issue(report, "blocker", "body_read_allowed_not_false", f"body_read_allowed must be False for {endpoint}", data.get("body_read_allowed"))

    report["payload_contracts"] = payload_contracts


def _audit_action_labels(report: dict[str, Any]) -> None:
    try:
        from runtime_core.api.dashboard_actions_registry_routes import build_dashboard_actions_registry

        payload = build_dashboard_actions_registry()
    except Exception:
        _record_issue(report, "blocker", "action_registry_import_failed", "Could not import/build dashboard action registry.", traceback.format_exc())
        report["action_registry"] = {"available": False}
        return

    actions = payload.get("actions") if isinstance(payload.get("actions"), list) else []
    labels = [str(action.get("label", "")) for action in actions]
    stage_like = [label for label in labels if re.match(r"^S\d+(?:\s|[-â€“]|$)", label)]

    if not actions:
        _record_issue(report, "blocker", "no_registered_actions", "Dashboard action registry has no actions.")
    if stage_like:
        _record_issue(report, "blocker", "stage_code_action_labels", "Action labels still look like build-stage codes.", stage_like)
    if "Plan a governed search" not in labels and "Compile search plan" not in labels:
        _record_issue(report, "warning", "missing_legacy_expected_plan_label", "Legacy tests expect a user-facing governed search label.", labels[:10])

    visual = payload.get("visual_contract", {}) if isinstance(payload.get("visual_contract"), dict) else {}
    for key, expected in [
        ("actions_tab_should_show_controls", True),
        ("actions_chip_should_be_greater_than_zero", True),
        ("unlock_allowed", False),
    ]:
        if visual.get(key) is not expected:
            _record_issue(report, "blocker", "visual_contract_mismatch", f"visual_contract.{key} expected {expected}.", visual)

    if payload.get("unlock_allowed") is not False:
        _record_issue(report, "blocker", "top_level_unlock_allowed_mismatch", "Action registry top-level unlock_allowed must be False.", payload.get("unlock_allowed"))

    report["action_registry"] = {
        "available": True,
        "action_count": len(actions),
        "labels": labels,
        "stage_like_labels": stage_like,
        "visual_contract": visual,
        "unlock_allowed": payload.get("unlock_allowed"),
    }


def _audit_frontend_assets(root: Path, report: dict[str, Any]) -> None:
    frontend: dict[str, Any] = {}
    for rel in EXPECTED_FRONTEND_ASSETS:
        path = root / rel
        text = _read_text(path) if path.exists() else ""
        frontend[rel] = {
            "exists": path.exists(),
            "size": len(text),
            "contains_fetch": "fetch(" in text,
            "contains_post_method": 'method: "POST"' in text or "method: 'POST'" in text,
            "contains_dot_post": ".post(" in text,
        }

    index_path = root / "frontend/command_center/modern/index.html"
    index_text = _read_text(index_path)
    required_mounts = [
        "dashboard_operator_console_contract.js",
        "dashboard_operator_console_contract.css",
    ]
    mounted = {asset: asset in index_text for asset in required_mounts}
    for asset, exists in mounted.items():
        if not exists:
            _record_issue(report, "warning", "frontend_asset_not_mounted", f"Expected active index.html to mount {asset}.")

    review_only_assets = {
        "frontend/command_center/modern/dashboard_operator_console_contract.js",
        "frontend/command_center/modern/dashboard_operator_console_contract.css",
    }
    for rel, info in frontend.items():
        if rel in review_only_assets and (info["contains_post_method"] or info["contains_dot_post"]):
            _record_issue(report, "blocker", "frontend_asset_contains_post", f"Frontend asset contains POST-like behavior: {rel}", info)

    report["frontend"] = {
        "assets": frontend,
        "index_mounts": mounted,
        "index_path": "frontend/command_center/modern/index.html",
    }


def _audit_static_source_risks(root: Path, report: dict[str, Any]) -> None:
    risk_patterns = {
        "subprocess": re.compile(r"\bsubprocess\b"),
        "os_system": re.compile(r"\bos\.system\s*\("),
        "eval": re.compile(r"\beval\s*\("),
        "exec": re.compile(r"\bexec\s*\("),
        "requests_network": re.compile(r"\brequests\.(get|post|put|patch|delete)\s*\("),
        "httpx_network": re.compile(r"\bhttpx\.(get|post|put|patch|delete)\s*\("),
        "urllib_network": re.compile(r"\burllib\.request\.urlopen\s*\("),
        "playwright_browser": re.compile(r"\bplaywright\b"),
        "selenium_browser": re.compile(r"\bselenium\b"),
    }
    active_roots = [root / "runtime_core", root / "frontend"]
    findings: list[dict[str, Any]] = []

    for base in active_roots:
        if not base.exists():
            continue
        for path in list(base.rglob("*.py")) + list(base.rglob("*.js")):
            rel = _rel(root, path)
            if any(part in rel for part in ["backups/", "archive/", "__pycache__/", ".pytest_cache/"]):
                continue
            text = _read_text(path)
            for name, pattern in risk_patterns.items():
                if pattern.search(text):
                    findings.append({"file": rel, "risk": name})

    reviewed_files: set[str] = set()
    review_payload: dict[str, Any] = {}
    try:
        from runtime_core.audit.risk_pattern_governance_review import build_risk_pattern_review, reviewed_risk_files

        reviewed_files = set(reviewed_risk_files())
        review_payload = build_risk_pattern_review()
    except Exception as exc:
        review_payload = {"status": "unavailable", "error": f"{type(exc).__name__}: {exc}"}

    reviewed_findings = [finding for finding in findings if finding.get("file") in reviewed_files]
    unreviewed_findings = [finding for finding in findings if finding.get("file") not in reviewed_files]

    if unreviewed_findings:
        _record_issue(
            report,
            "warning",
            "active_source_risk_patterns",
            "Active source contains unreviewed risky execution/network/browser strings that should be reviewed.",
            unreviewed_findings[:80],
        )

    report["static_risk_scan"] = {
        "finding_count": len(findings),
        "reviewed_finding_count": len(reviewed_findings),
        "unreviewed_finding_count": len(unreviewed_findings),
        "all_findings_reviewed": len(unreviewed_findings) == 0,
        "review_status": review_payload.get("status"),
        "review_version": review_payload.get("version"),
        "reviewed_files": sorted(reviewed_files),
        "findings": findings[:200],
        "reviewed_findings": reviewed_findings[:200],
        "unreviewed_findings": unreviewed_findings[:200],
    }


def _summarize(report: dict[str, Any]) -> None:
    issues = report.get("issues", [])
    blockers = [issue for issue in issues if issue.get("severity") == "blocker"]
    warnings = [issue for issue in issues if issue.get("severity") == "warning"]
    report["summary"] = {
        "audit_version": AUDIT_VERSION,
        "generated_at": report.get("generated_at"),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "plateau_status": "blocked" if blockers else "ready",
        "forward_motion_allowed": len(blockers) == 0,
        "next_step": "Repair blockers before forward builds." if blockers else "Plateau is clean enough to continue to next dashboard/operator build.",
    }


def _write_markdown(report: dict[str, Any], json_path: Path) -> Path:
    md_path = json_path.with_suffix(".md")
    summary = report.get("summary", {})
    lines = [
        f"# Claire System Plateau Audit",
        "",
        f"- Version: `{summary.get('audit_version')}`",
        f"- Generated: `{summary.get('generated_at')}`",
        f"- Plateau status: **{summary.get('plateau_status')}**",
        f"- Forward motion allowed: **{summary.get('forward_motion_allowed')}**",
        f"- Blockers: **{summary.get('blocker_count')}**",
        f"- Warnings: **{summary.get('warning_count')}**",
        "",
        "## Issues",
        "",
    ]
    issues = report.get("issues", [])
    if not issues:
        lines.append("No blockers or warnings were detected by this audit.")
    else:
        for issue in issues:
            lines.append(f"- **{issue.get('severity')}** `{issue.get('code')}` â€” {issue.get('message')}")
    lines.extend(
        [
            "",
            "## Key route checks",
            "",
        ]
    )
    routes = report.get("routes", {}).get("expected_get", {})
    for path, data in routes.items():
        lines.append(f"- `{path}` â†’ `{data.get('status_code', data.get('error'))}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path


def run_audit(root: Path | None = None, *, write_report: bool = True) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve()
    report: dict[str, Any] = {
        "audit_version": AUDIT_VERSION,
        "generated_at": _utc_now(),
        "root": str(root),
        "python": sys.version,
        "issues": [],
    }

    _audit_paths(root, report)
    _audit_python_syntax(root, report)
    _audit_environment(report)
    _audit_routes(root, report)
    _audit_payloads(report)
    _audit_action_labels(report)
    _audit_frontend_assets(root, report)
    _audit_static_source_risks(root, report)
    _summarize(report)

    if write_report:
        reports_dir = root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = reports_dir / f"S1153_S1180_SYSTEM_PLATEAU_AUDIT_{stamp}.json"
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path = _write_markdown(report, json_path)
        report["report_paths"] = {
            "json": str(json_path),
            "markdown": str(md_path),
        }
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    fail_on_blockers = "--fail-on-blockers" in argv
    report = run_audit(Path.cwd(), write_report=True)
    summary = report["summary"]

    print("[Claire System Plateau Audit]")
    print(f"Version: {AUDIT_VERSION}")
    print(f"Status: {summary['plateau_status']}")
    print(f"Blockers: {summary['blocker_count']}")
    print(f"Warnings: {summary['warning_count']}")
    print(f"Forward motion allowed: {summary['forward_motion_allowed']}")
    if "report_paths" in report:
        print(f"JSON report: {report['report_paths']['json']}")
        print(f"Markdown report: {report['report_paths']['markdown']}")

    if report.get("issues"):
        print("\nTop issues:")
        for issue in report["issues"][:20]:
            print(f"- {issue['severity']} {issue['code']}: {issue['message']}")

    if fail_on_blockers and summary["blocker_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
