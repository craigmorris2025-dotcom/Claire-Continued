
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.80"
CONTRACT_NAME = "Launch Candidate Freeze"

FREEZE_PATH = Path("data/launch_candidate/v17_80_launch_candidate_freeze.json")
MANIFEST_PATH = Path("data/launch_candidate/launch_candidate_manifest.json")
PROTECTED_PATHS_PATH = Path("data/launch_candidate/protected_paths_manifest.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/launch_candidate_freeze_payload.json")
STOP_GO_PATH = Path("data/launch_candidate/v17_80_launch_candidate_stop_go.json")
STOP_GO_MD_PATH = Path("data/launch_candidate/v17_80_launch_candidate_stop_go.md")
FREEZE_README_PATH = Path("data/launch_candidate/README_LAUNCH_CANDIDATE_FREEZE.md")

PRIOR_PROOF_REPORTS = {
    "v17_75_e2e_proof": "data/proof/full_end_to_end_proof_pack.json",
    "v17_76_platform_smoke": "data/proof/platform_endpoint_smoke_proof.json",
    "v17_77_launch_hardening": "data/launch_hardening/platform_launch_hardening_report.json",
    "v17_78_desktop_startup": "data/desktop_packaging/startup_reliability_report.json",
    "v17_79_manual_browser_swagger": "data/proof/manual_browser_swagger_proof_binder.json",
}

PROTECTED_PATHS = [
    "claire/app.py",
    "claire/api",
    "claire/dashboard",
    "claire/operator",
    "claire/proof",
    "claire/platform",
    "claire/desktop",
    "claire/runtime_truth",
    "claire/routing",
    "claire/autodesign",
    "claire/design_portal",
    "claire/validation_stack",
    "claire/internet_readiness",
    "claire/update_governance",
    "frontend/command_center/modern/index.html",
    "frontend/command_center/modern/claire_workspace_agent_dashboard.css",
    "frontend/command_center/modern/claire_workspace_agent_dashboard.js",
    "LAUNCH_PLATFORM.bat",
    "START_CLAIRE_SAFE.bat",
    "VERIFY_CLAIRE_STARTUP.bat",
    "OPEN_CLAIRE_PROOF_URLS.bat",
    "data/runtime/runtime_truth_canonical.json",
    "data/dashboard/operator_dashboard_state.json",
    "data/operator/search_command/search_command_capabilities.json",
    "data/proof/full_end_to_end_proof_pack.json",
    "data/proof/platform_endpoint_smoke_proof.json",
    "data/proof/manual_browser_swagger_proof_binder.json",
    "data/launch_hardening/platform_launch_hardening_report.json",
    "data/desktop_packaging/startup_reliability_report.json",
    "data/update_packs/update_governance_regression_lock.json",
]

FREEZE_RULES = {
    "no_cleanup_or_delete_without_freeze_review": True,
    "no_backend_folder_delete_yet": True,
    "no_dashboard_shell_replacement_without_bridge_test": True,
    "no_launcher_rewrite_without_startup_test": True,
    "no_route_removal_without_endpoint_smoke_test": True,
    "no_runtime_truth_contract_change_without_dashboard_state_test": True,
    "no_web_search_live_enablement": True,
    "no_automatic_update_execution": True,
    "no_autonomous_agent_execution": True,
    "manual_browser_swagger_proof_required_before_public_launch": True,
}

NEXT_ALLOWED_BUILDS = [
    "v17.81 Cleanup Proof Before Archive/Delete",
    "v17.82 Launch Candidate Repair Pack if manual proof finds blockers",
    "v17.83 Internet Provider Configuration Gate",
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


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def path_inventory(root: Path, relative: str) -> Dict[str, Any]:
    path = root / relative
    item = {
        "path": relative,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }
    if path.exists() and path.is_file():
        item["size_bytes"] = path.stat().st_size
        item["sha256"] = sha256_file(path)
    elif path.exists() and path.is_dir():
        try:
            files = [p for p in path.rglob("*") if p.is_file()]
            item["file_count"] = len(files)
            item["total_size_bytes"] = sum(p.stat().st_size for p in files[:5000])
            item["count_limited"] = len(files) > 5000
        except Exception as exc:
            item["scan_error"] = str(exc)
    return item


def load_prior_reports(root: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, rel_path in PRIOR_PROOF_REPORTS.items():
        payload, source = read_json(root / rel_path)
        stop_go = payload.get("stop_go") if isinstance(payload.get("stop_go"), dict) else {}
        status = payload.get("status") or stop_go.get("status") or "missing"
        out[name] = {
            "path": rel_path,
            "source": source,
            "status": status,
            "stop_go_status": stop_go.get("status", status),
            "recommendation": stop_go.get("recommendation") or payload.get("recommendation", ""),
        }
    return out


def build_protected_paths_manifest(root: Path) -> Dict[str, Any]:
    manifest = {
        "version": VERSION,
        "generated_at": now(),
        "purpose": "Paths protected by the launch-candidate freeze. Do not delete, archive, or replace these without a follow-up proof pass.",
        "protected_paths": [path_inventory(root, relative) for relative in PROTECTED_PATHS],
        "rules": FREEZE_RULES,
    }
    write_json(root / PROTECTED_PATHS_PATH, manifest)
    return manifest


def assess_manual_proof(root: Path) -> Dict[str, Any]:
    evidence, source = read_json(root / "data/proof/manual_browser_swagger_evidence_template.json")
    if not evidence:
        return {
            "source": source,
            "status": "not_started",
            "required_slots": 0,
            "passed_slots": 0,
            "failed_slots": 0,
            "not_checked_slots": 0,
            "manual_final_review_status": "not_checked",
        }

    slots = evidence.get("evidence_slots") if isinstance(evidence.get("evidence_slots"), list) else []
    required = [slot for slot in slots if isinstance(slot, dict) and slot.get("required")]
    passed = [slot for slot in required if slot.get("operator_status") == "passed"]
    failed = [slot for slot in required if slot.get("operator_status") == "failed"]
    warnings = [slot for slot in required if slot.get("operator_status") == "warning"]
    not_checked = [slot for slot in required if slot.get("operator_status") == "not_checked"]
    final_review = evidence.get("operator_final_review") if isinstance(evidence.get("operator_final_review"), dict) else {}

    if failed:
        status = "failed"
    elif not_checked:
        status = "incomplete"
    elif warnings:
        status = "warning"
    else:
        status = "passed"

    return {
        "source": source,
        "status": status,
        "required_slots": len(required),
        "passed_slots": len(passed),
        "failed_slots": len(failed),
        "warning_slots": len(warnings),
        "not_checked_slots": len(not_checked),
        "manual_final_review_status": final_review.get("status", "not_checked"),
    }


def safety_locks(root: Path) -> Dict[str, Any]:
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
        "search_automatic_updates_disabled": live_web.get("current_automatic_updates_enabled", False) is False,
    }
    return {
        "status": "passed" if all(checks.values()) else "blocked",
        "checks": checks,
    }


def determine_stop_go(priors: Dict[str, Any], protected: Dict[str, Any], manual: Dict[str, Any], safety: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    for name, report in priors.items():
        if report.get("source", {}).get("status") != "loaded":
            blockers.append(f"missing_prior_report:{name}")
        if report.get("status") == "STOP":
            warnings.append(f"prior_report_stop:{name}")

    missing_protected = [
        item["path"] for item in protected.get("protected_paths", [])
        if item.get("exists") is not True
    ]
    for path in missing_protected:
        if path.startswith("data/") or path.endswith(".bat") or path.endswith(".html") or path == "claire/app.py":
            blockers.append(f"missing_protected_path:{path}")
        else:
            warnings.append(f"missing_protected_path:{path}")

    if safety.get("status") != "passed":
        blockers.append("safety_locks_failed")

    if manual.get("status") in {"not_started", "incomplete"}:
        warnings.append("manual_browser_swagger_evidence_not_complete")
    elif manual.get("status") == "failed":
        blockers.append("manual_browser_swagger_evidence_failed")
    elif manual.get("status") == "warning":
        warnings.append("manual_browser_swagger_evidence_has_warnings")

    if blockers:
        status = "STOP"
        recommendation = "Do not freeze as launch candidate until blockers are fixed."
    elif warnings:
        status = "FROZEN_WITH_WARNINGS_MANUAL_PROOF_REQUIRED"
        recommendation = "Launch candidate freeze is created, but manual proof/warnings must be resolved before public launch."
    else:
        status = "FROZEN_GO_TO_RELEASE_CANDIDATE_REVIEW"
        recommendation = "Launch candidate is frozen. Proceed only to release-candidate review or controlled repair builds."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
    }


def write_markdown(root: Path, freeze: Dict[str, Any]) -> None:
    sg = freeze["stop_go"]
    lines = [
        "# Claire v17.80 Launch Candidate Freeze",
        "",
        f"Generated: {freeze['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Freeze Rules",
        "",
    ]
    for key, value in FREEZE_RULES.items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Protected Paths",
        "",
    ])
    for item in freeze["protected_paths_manifest"].get("protected_paths", []):
        mark = "âœ…" if item.get("exists") else "âŒ"
        lines.append(f"- {mark} `{item.get('path')}`")
    lines.extend([
        "",
        "## Prior Reports",
        "",
    ])
    for name, report in freeze["prior_reports"].items():
        lines.append(f"- **{name}**: {report.get('status')} ({report.get('source', {}).get('status')})")
    lines.extend([
        "",
        "## Manual Proof",
        "",
        f"- Status: {freeze['manual_proof'].get('status')}",
        f"- Required slots: {freeze['manual_proof'].get('required_slots')}",
        f"- Not checked slots: {freeze['manual_proof'].get('not_checked_slots')}",
        "",
        "## Next Allowed Builds",
        "",
    ])
    for item in NEXT_ALLOWED_BUILDS:
        lines.append(f"- {item}")
    if sg["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for item in sg["blockers"]:
            lines.append(f"- {item}")
    if sg["warnings"]:
        lines.extend(["", "## Warnings", ""])
        for item in sg["warnings"]:
            lines.append(f"- {item}")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))
    write_text(root / FREEZE_README_PATH, "\n".join(lines))


def build_launch_candidate_freeze(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    protected = build_protected_paths_manifest(root)
    priors = load_prior_reports(root)
    manual = assess_manual_proof(root)
    safety = safety_locks(root)
    stop_go = determine_stop_go(priors, protected, manual, safety)

    freeze = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "prior_reports": priors,
        "manual_proof": manual,
        "safety_locks": safety,
        "protected_paths_manifest": protected,
        "freeze_rules": FREEZE_RULES,
        "allowed_next_builds": NEXT_ALLOWED_BUILDS,
        "governance": {
            "launch_candidate_frozen": True,
            "cleanup_requires_freeze_review": True,
            "deletion_requires_proof_pass": True,
            "public_launch_not_approved_by_freeze_alone": True,
            "manual_browser_swagger_proof_required": True,
            "live_internet_disabled": True,
            "automatic_updates_disabled": True,
            "autonomous_agent_execution_disabled": True,
        },
    }

    manifest = {
        "version": VERSION,
        "generated_at": freeze["generated_at"],
        "candidate_name": "Claire Syntalion v17.80 Launch Candidate",
        "candidate_status": freeze["status"],
        "freeze_file": str(FREEZE_PATH).replace("\\", "/"),
        "protected_paths_file": str(PROTECTED_PATHS_PATH).replace("\\", "/"),
        "stop_go_file": str(STOP_GO_PATH).replace("\\", "/"),
        "manual_proof_status": manual.get("status"),
        "prior_report_status": {name: item.get("status") for name, item in priors.items()},
        "next_allowed_builds": NEXT_ALLOWED_BUILDS,
    }

    write_json(root / FREEZE_PATH, freeze)
    write_json(root / MANIFEST_PATH, manifest)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": freeze["generated_at"], **stop_go})
    write_markdown(root, freeze)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": freeze["generated_at"],
        "status": freeze["status"],
        "recommendation": stop_go["recommendation"],
        "blockers": stop_go["blockers"],
        "warnings": stop_go["warnings"],
        "manual_proof": manual,
        "safety_locks": safety,
        "protected_path_count": len(PROTECTED_PATHS),
        "next_allowed_builds": NEXT_ALLOWED_BUILDS,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return freeze


def launch_candidate_freeze_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    freeze = build_launch_candidate_freeze(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": freeze.get("status"),
        "recommendation": freeze.get("stop_go", {}).get("recommendation"),
        "blockers": freeze.get("stop_go", {}).get("blockers", []),
        "warnings": freeze.get("stop_go", {}).get("warnings", []),
        "manual_proof_status": freeze.get("manual_proof", {}).get("status"),
        "launch_candidate_frozen": True,
        "next_allowed_builds": NEXT_ALLOWED_BUILDS,
    }
