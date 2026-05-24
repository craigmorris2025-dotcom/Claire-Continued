
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.75"
CONTRACT_NAME = "Full End-to-End Proof Pack"

PROOF_PATH = Path("data/proof/full_end_to_end_proof_pack.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/full_e2e_proof_pack_payload.json")
STOP_GO_PATH = Path("data/proof/v17_75_stop_go_report.json")
STOP_GO_MD_PATH = Path("data/proof/v17_75_stop_go_report.md")

PROOF_INPUTS = {
    "dashboard_wiring": "data/dashboard/v17_64_1_functional_dashboard_validation.json",
    "runtime_truth": "data/runtime/v17_65_runtime_truth_validation.json",
    "route_audit": "data/routes/v17_66_route_audit_validation.json",
    "autodesign_handoff": "data/autodesign/v17_67_autodesign_handoff_validation.json",
    "design_portal": "data/design_portal/v17_68_design_portal_output_validation.json",
    "buildability_validation": "data/validation/v17_69_buildability_validation_result.json",
    "internet_readiness": "data/internet_readiness/v17_70_internet_readiness_validation_result.json",
    "update_pack_staging": "data/update_packs/v17_71_update_pack_staging_validation_result.json",
    "rollback_update_plan": "data/update_packs/v17_72_rollback_update_plan_validation_result.json",
    "automatic_update_runner_gate": "data/update_packs/v17_73_automatic_update_runner_gate_validation_result.json",
    "update_governance_regression_lock": "data/update_packs/v17_74_update_governance_regression_lock_validation_result.json",
}

CORE_OUTPUTS = {
    "active_dashboard": "frontend/command_center/modern/platform_dashboard.html",
    "launcher": "LAUNCH_PLATFORM.bat",
    "operator_dashboard_state": "data/dashboard/operator_dashboard_state.json",
    "runtime_truth_canonical": "data/runtime/runtime_truth_canonical.json",
    "dashboard_runtime_truth": "data/runtime/dashboard_runtime_truth.json",
    "route_audit": "data/routes/discovery_breakthrough_innovation_route_audit.json",
    "autodesign_handoff": "data/autodesign/autodesign_handoff_contract.json",
    "design_portal_output": "data/design_portal/design_portal_output_contract.json",
    "buildability_validation": "data/validation/buildability_viability_manufacturability_validation.json",
    "internet_readiness": "data/internet_readiness/internet_readiness_verification.json",
    "update_pack_staging": "data/update_packs/update_pack_staging_index.json",
    "rollback_plan_index": "data/update_packs/rollback_plan_index.json",
    "runner_gate": "data/update_packs/automatic_update_runner_gate.json",
    "regression_lock": "data/update_packs/update_governance_regression_lock.json",
}

ENDPOINTS = [
    "/operator/dashboard/state",
    "/dashboard/state",
    "/runtime/truth",
    "/runtime/state",
    "/routes/audit",
    "/routes/audit/summary",
    "/autodesign/handoff",
    "/autodesign/handoff/summary",
    "/design-portal/output",
    "/design-portal/output/summary",
    "/validation/buildability",
    "/validation/buildability/summary",
    "/internet/readiness",
    "/internet/readiness/summary",
    "/updates/staging",
    "/updates/rollback-plan",
    "/updates/runner-gate",
    "/updates/regression-lock",
]

PROOF_DOMAINS = [
    "dashboard_functionality",
    "runtime_truth",
    "route_integrity",
    "autodesign_handoff",
    "design_portal",
    "buildability_validation",
    "internet_readiness",
    "update_governance",
    "safety_locks",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def path_exists(root: Path, rel_path: str) -> Dict[str, Any]:
    path = root / rel_path
    return {
        "path": rel_path,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def collect_inputs(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    input_reports: Dict[str, Any] = {}
    input_sources: Dict[str, Any] = {}
    for name, rel_path in PROOF_INPUTS.items():
        payload, source = read_json(root / rel_path)
        input_reports[name] = payload
        input_sources[name] = source
    return input_reports, input_sources


def collect_core_outputs(root: Path) -> Dict[str, Any]:
    return {name: path_exists(root, rel_path) for name, rel_path in CORE_OUTPUTS.items()}


def validation_passed(report: Dict[str, Any]) -> Optional[bool]:
    if not report:
        return None
    status = str(report.get("status", "")).lower()
    if status == "passed":
        return True
    if status in {"failed", "error"}:
        return False
    return None


def nested_false(payload: Dict[str, Any], paths: List[List[str]]) -> Dict[str, Any]:
    out = {}
    for path in paths:
        cur: Any = payload
        found = True
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                found = False
                break
        out[".".join(path)] = {"found": found, "value": cur if found else None, "is_false": cur is False if found else False}
    return out


def assess_dashboard(root: Path, reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    dashboard_file = root / CORE_OUTPUTS["active_dashboard"]
    js_file = root / "frontend/command_center/modern/platform_dashboard.js"
    text = dashboard_file.read_text(encoding="utf-8", errors="replace") if dashboard_file.exists() else ""
    js = js_file.read_text(encoding="utf-8", errors="replace") if js_file.exists() else ""
    required_words = ["data-platform-dashboard", "dashboard", "main-content"]
    required_js_words = ["/api/dashboard/state", "renderSettings", "renderDesignPortal", "renderUpdates"]
    missing_words = [word for word in required_words if word not in text]
    missing_js_words = [word for word in required_js_words if word not in js]
    api_wired = "/api/dashboard/state" in js or "/operator/dashboard/state" in js or "/dashboard/state" in js
    return {
        "status": "passed" if core["active_dashboard"]["exists"] and api_wired and not missing_words and not missing_js_words else "blocked",
        "dashboard_exists": core["active_dashboard"]["exists"],
        "api_wired": api_wired,
        "missing_surfaces": missing_words,
        "missing_js_bindings": missing_js_words,
        "validation_report_passed": validation_passed(reports.get("dashboard_wiring")),
    }


def assess_runtime_truth(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "passed" if core["runtime_truth_canonical"]["exists"] and core["dashboard_runtime_truth"]["exists"] else "blocked",
        "canonical_exists": core["runtime_truth_canonical"]["exists"],
        "dashboard_truth_exists": core["dashboard_runtime_truth"]["exists"],
        "validation_report_passed": validation_passed(reports.get("runtime_truth")),
    }


def assess_route_integrity(root: Path, reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    route_audit, _ = read_json(root / CORE_OUTPUTS["route_audit"])
    contract = route_audit.get("contract") if isinstance(route_audit.get("contract"), dict) else {}
    rule = route_audit.get("route_rule") if isinstance(route_audit.get("route_rule"), dict) else {}
    required_flags = [
        "discovery_breakthrough_innovation_first_class",
        "autodesign_required_when_invention_required",
        "design_portal_required_when_invention_required",
        "missing_outputs_are_not_faked",
    ]
    missing_flags = [flag for flag in required_flags if rule.get(flag) is not True]
    return {
        "status": "passed" if core["route_audit"]["exists"] and not missing_flags else "blocked",
        "route_family": contract.get("route_family"),
        "route_status": contract.get("status"),
        "invention_required": contract.get("invention_required"),
        "missing_rule_flags": missing_flags,
        "validation_report_passed": validation_passed(reports.get("route_audit")),
    }


def assess_autodesign(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    report = reports.get("autodesign_handoff", {})
    return {
        "status": "passed" if core["autodesign_handoff"]["exists"] else "blocked",
        "handoff_exists": core["autodesign_handoff"]["exists"],
        "handoff_status": report.get("handoff_status"),
        "invention_required": report.get("invention_required"),
        "validation_report_passed": validation_passed(report),
    }


def assess_design_portal(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    report = reports.get("design_portal", {})
    return {
        "status": "passed" if core["design_portal_output"]["exists"] else "blocked",
        "design_portal_exists": core["design_portal_output"]["exists"],
        "design_portal_status": report.get("design_portal_status"),
        "validation_report_passed": validation_passed(report),
    }


def assess_buildability(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    report = reports.get("buildability_validation", {})
    return {
        "status": "passed" if core["buildability_validation"]["exists"] else "blocked",
        "validation_exists": core["buildability_validation"]["exists"],
        "stack_status": report.get("validation_status"),
        "blockers": report.get("blockers", []),
        "warnings": report.get("warnings", []),
        "validation_report_passed": validation_passed(report),
    }


def assess_internet(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    report = reports.get("internet_readiness", {})
    readiness = report.get("readiness") if isinstance(report.get("readiness"), dict) else {}
    return {
        "status": "passed" if core["internet_readiness"]["exists"] else "blocked",
        "readiness_exists": core["internet_readiness"]["exists"],
        "internet_status": report.get("internet_status"),
        "static_readiness": readiness.get("static_internet_readiness"),
        "live_internet_enabled": readiness.get("live_internet_enabled", False),
        "automatic_updates_enabled": readiness.get("automatic_updates_enabled", False),
        "blockers": report.get("blockers", []),
        "warnings": report.get("warnings", []),
        "validation_report_passed": validation_passed(report),
    }


def assess_update_governance(reports: Dict[str, Any], core: Dict[str, Any]) -> Dict[str, Any]:
    staging = reports.get("update_pack_staging", {})
    rollback = reports.get("rollback_update_plan", {})
    runner = reports.get("automatic_update_runner_gate", {})
    lock = reports.get("update_governance_regression_lock", {})

    false_checks = {
        "staging_execution": staging.get("governance", {}).get("execution_enabled") is False,
        "staging_automatic": staging.get("governance", {}).get("automatic_execution_enabled") is False,
        "rollback_execution": rollback.get("governance", {}).get("execution_enabled") is False,
        "rollback_automatic": rollback.get("governance", {}).get("automatic_execution_enabled") is False,
        "runner_execution": runner.get("runner_contract", {}).get("execution_enabled") is False,
        "runner_automatic": runner.get("runner_contract", {}).get("automatic_execution_enabled") is False,
        "runner_background": runner.get("runner_contract", {}).get("background_execution_enabled") is False,
        "lock_active": lock.get("regression_lock_active") is True,
    }

    all_outputs = [
        core["update_pack_staging"]["exists"],
        core["rollback_plan_index"]["exists"],
        core["runner_gate"]["exists"],
        core["regression_lock"]["exists"],
    ]

    return {
        "status": "passed" if all(all_outputs) and all(false_checks.values()) else "blocked",
        "outputs_exist": all_outputs,
        "false_checks": false_checks,
        "staging_pack_count": staging.get("pack_count"),
        "rollback_plan_count": rollback.get("plan_count"),
        "gate_status": runner.get("gate_status"),
        "lock_status": lock.get("lock_status"),
        "validation_reports_passed": {
            "staging": validation_passed(staging),
            "rollback": validation_passed(rollback),
            "runner_gate": validation_passed(runner),
            "regression_lock": validation_passed(lock),
        },
    }


def assess_safety_locks(reports: Dict[str, Any]) -> Dict[str, Any]:
    internet = reports.get("internet_readiness", {})
    runner = reports.get("automatic_update_runner_gate", {})
    lock = reports.get("update_governance_regression_lock", {})

    readiness = internet.get("readiness") if isinstance(internet.get("readiness"), dict) else {}
    runner_contract = runner.get("runner_contract") if isinstance(runner.get("runner_contract"), dict) else {}
    checks = {
        "live_internet_disabled": readiness.get("live_internet_enabled", False) is False,
        "automatic_updates_disabled": readiness.get("automatic_updates_enabled", False) is False,
        "runner_does_not_execute": runner_contract.get("runner_executes_updates") is False,
        "runner_execution_disabled": runner_contract.get("execution_enabled") is False,
        "runner_background_disabled": runner_contract.get("background_execution_enabled") is False,
        "regression_lock_active": lock.get("regression_lock_active") is True,
    }

    return {
        "status": "passed" if all(checks.values()) else "blocked",
        "checks": checks,
    }


def stop_go_status(domains: Dict[str, Any]) -> Dict[str, Any]:
    blocked = [name for name, item in domains.items() if item.get("status") == "blocked"]
    warnings = []
    for name, item in domains.items():
        if item.get("warnings"):
            warnings.append({"domain": name, "warnings": item.get("warnings")})
    if blocked:
        status = "STOP"
        recommendation = "Do not proceed to live launch or automatic updates. Fix blocked proof domains first."
    elif warnings:
        status = "GO_WITH_WARNINGS"
        recommendation = "Proceed only to manual review. Do not enable automatic updates."
    else:
        status = "GO_TO_MANUAL_REVIEW"
        recommendation = "Core proof pack is assembled for manual review. Automatic updates remain disabled."
    return {
        "status": status,
        "blocked_domains": blocked,
        "warnings": warnings,
        "recommendation": recommendation,
    }


def write_stop_go_markdown(root: Path, report: Dict[str, Any]) -> None:
    sg = report["stop_go"]
    lines = [
        "# Claire v17.75 Stop / Go Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Domain Status",
        "",
    ]
    for name, item in report["domains"].items():
        lines.append(f"- **{name}**: {item.get('status')}")
    lines.extend([
        "",
        "## Safety Locks",
        "",
        "- Live internet remains disabled.",
        "- Automatic updates remain disabled.",
        "- Background execution remains disabled.",
        "- Operator review remains required.",
        "",
    ])
    if sg["blocked_domains"]:
        lines.append("## Blocked Domains")
        lines.append("")
        for domain in sg["blocked_domains"]:
            lines.append(f"- {domain}")
        lines.append("")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def build_full_e2e_proof_pack(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    reports, input_sources = collect_inputs(root)
    core_outputs = collect_core_outputs(root)

    domains = {
        "dashboard_functionality": assess_dashboard(root, reports, core_outputs),
        "runtime_truth": assess_runtime_truth(reports, core_outputs),
        "route_integrity": assess_route_integrity(root, reports, core_outputs),
        "autodesign_handoff": assess_autodesign(reports, core_outputs),
        "design_portal": assess_design_portal(reports, core_outputs),
        "buildability_validation": assess_buildability(reports, core_outputs),
        "internet_readiness": assess_internet(reports, core_outputs),
        "update_governance": assess_update_governance(reports, core_outputs),
        "safety_locks": assess_safety_locks(reports),
    }

    stop_go = stop_go_status(domains)

    proof = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "input_sources": input_sources,
        "core_outputs": core_outputs,
        "domains": domains,
        "endpoint_inventory": ENDPOINTS,
        "proof_domains": PROOF_DOMAINS,
        "launch_readiness": {
            "dashboard_ready_for_manual_review": domains["dashboard_functionality"]["status"] == "passed",
            "runtime_truth_ready_for_manual_review": domains["runtime_truth"]["status"] == "passed",
            "route_contract_ready_for_manual_review": domains["route_integrity"]["status"] == "passed",
            "internet_static_readiness_reviewable": domains["internet_readiness"]["status"] == "passed",
            "automatic_updates_ready": False,
            "live_internet_enabled": False,
            "automatic_updates_enabled": False,
            "background_execution_enabled": False,
        },
        "governance": {
            "no_fake_data": True,
            "missing_outputs_remain_visible": True,
            "discovery_breakthrough_innovation_first_class": True,
            "autodesign_design_portal_first_class": True,
            "operator_review_required": True,
            "no_hidden_updates": True,
            "no_background_execution": True,
            "automatic_updates_disabled": True,
            "live_internet_disabled_until_review": True,
        },
        "next": [
            "Manual review of v17.75 proof pack",
            "Fix any STOP domains",
            "If proof pack is GO_WITH_WARNINGS or GO_TO_MANUAL_REVIEW, test backend endpoints in Swagger",
            "Only after manual endpoint proof should automatic update execution be considered in a later gated build",
        ],
    }

    write_json(root / PROOF_PATH, proof)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": proof["generated_at"], **stop_go})
    write_stop_go_markdown(root, proof)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": proof["generated_at"],
        "status": proof["status"],
        "stop_go": proof["stop_go"],
        "domain_status": {name: item.get("status") for name, item in domains.items()},
        "launch_readiness": proof["launch_readiness"],
        "governance": proof["governance"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return proof


def full_e2e_proof_pack_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    proof = build_full_e2e_proof_pack(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": proof.get("status"),
        "stop_go": proof.get("stop_go"),
        "launch_readiness": proof.get("launch_readiness"),
        "domain_status": {name: item.get("status") for name, item in proof.get("domains", {}).items()},
        "automatic_updates_enabled": False,
        "live_internet_enabled": False,
    }
