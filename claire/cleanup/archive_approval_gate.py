
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.82"
CONTRACT_NAME = "Archive Approval Gate + Safe Archive Executor Prepared"

CLEANUP_REPORT_PATH = Path("data/cleanup/cleanup_proof_before_archive_delete.json")
ARCHIVE_PLAN_SOURCE_PATH = Path("data/cleanup/archive_plan_do_not_execute.json")
PROTECTED_CONFLICT_PATH = Path("data/cleanup/protected_path_conflict_report.json")
FREEZE_PATH = Path("data/launch_candidate/v17_80_launch_candidate_freeze.json")

GATE_PATH = Path("data/cleanup/archive_approval_gate.json")
APPROVAL_TEMPLATE_PATH = Path("data/cleanup/approved_archive_moves_template.json")
EXECUTION_LOCK_PATH = Path("data/cleanup/archive_execution_lock.json")
EXECUTION_REPORT_PATH = Path("data/cleanup/archive_execution_report.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/archive_approval_gate_payload.json")
STOP_GO_PATH = Path("data/cleanup/v17_82_archive_approval_stop_go.json")
STOP_GO_MD_PATH = Path("data/cleanup/v17_82_archive_approval_stop_go.md")
REVIEW_MD_PATH = Path("data/cleanup/ARCHIVE_APPROVAL_REVIEW.md")

APPROVAL_PHRASE = "ARCHIVE APPROVED"
ARCHIVE_ROOT = Path("archive_review_pending/v17_82")

FORBIDDEN_ARCHIVE_PREFIXES = [
    ".git",
    ".venv",
    "claire",
    "frontend/command_center/modern/index.html",
    "data/runtime",
    "data/dashboard/operator_dashboard_state.json",
    "data/launch_candidate",
    "LAUNCH_CLAIRE.bat",
    "START_CLAIRE_SAFE.bat",
    "VERIFY_CLAIRE_STARTUP.bat",
]

REQUIRED_POST_ARCHIVE_PROOFS = [
    "python -m pytest tests/test_v17_76_platform_endpoint_smoke_proof.py -q",
    "python -m pytest tests/test_v17_78_desktop_packaging_startup_reliability.py -q",
    "START_CLAIRE_SAFE.bat",
    "VERIFY_CLAIRE_STARTUP.bat",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_path(value: str) -> str:
    return str(value or "").replace("\\", "/").strip().strip("./")


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


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def path_exists(root: Path, relative: str) -> Dict[str, Any]:
    p = root / normalize_path(relative)
    return {
        "path": normalize_path(relative),
        "exists": p.exists(),
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
    }


def is_forbidden_path(path: str) -> Tuple[bool, List[str]]:
    p = normalize_path(path).rstrip("/")
    reasons = []
    for forbidden in FORBIDDEN_ARCHIVE_PREFIXES:
        f = normalize_path(forbidden).rstrip("/")
        if p == f or p.startswith(f + "/") or f.startswith(p + "/"):
            reasons.append(f)
    return bool(reasons), reasons


def load_archive_plan(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return read_json(root / ARCHIVE_PLAN_SOURCE_PATH)


def load_cleanup_report(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return read_json(root / CLEANUP_REPORT_PATH)


def archive_review_candidates(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = plan.get("archive_review_candidates")
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if isinstance(item, dict) and item.get("path"):
            out.append(item)
    return out


def build_approval_template(root: Path, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    entries = []
    for item in candidates:
        candidate_path = normalize_path(str(item.get("path", "")))
        forbidden, forbidden_reasons = is_forbidden_path(candidate_path)
        entries.append({
            "path": candidate_path,
            "approved": False,
            "operator_notes": "",
            "recommended_action": "archive_review_only",
            "eligible_for_approval": not forbidden,
            "blocked_reasons": forbidden_reasons,
            "source_classification": item.get("classification"),
            "source_reason": item.get("reason", []),
        })

    template = {
        "version": VERSION,
        "created_at": now(),
        "approval_phrase_required": APPROVAL_PHRASE,
        "operator_confirm_text": "",
        "archive_root": str(ARCHIVE_ROOT).replace("\\", "/"),
        "instructions": [
            "This file is a template. Nothing will move until operator_confirm_text equals ARCHIVE APPROVED.",
            "Set approved=true only for paths you reviewed manually.",
            "Do not approve protected paths, backend, claire, data/runtime, launchers, or active dashboard files.",
            "After any move, immediately run endpoint smoke proof and desktop startup proof.",
        ],
        "moves": entries,
        "execution_enabled": False,
        "delete_allowed": False,
        "automatic_execution_allowed": False,
    }
    write_json(root / APPROVAL_TEMPLATE_PATH, template)
    return template


def build_execution_lock(root: Path) -> Dict[str, Any]:
    lock = {
        "version": VERSION,
        "generated_at": now(),
        "execution_default": "locked",
        "archive_execution_enabled": False,
        "delete_enabled": False,
        "automatic_execution_enabled": False,
        "required_confirm_text": APPROVAL_PHRASE,
        "approval_file": str(APPROVAL_TEMPLATE_PATH).replace("\\", "/"),
        "post_archive_proofs_required": REQUIRED_POST_ARCHIVE_PROOFS,
        "rules": {
            "move_only_no_delete": True,
            "protected_paths_blocked": True,
            "forbidden_prefixes_blocked": True,
            "operator_approval_required": True,
            "endpoint_smoke_required_after_move": True,
            "desktop_startup_required_after_move": True,
            "rollback_by_move_back_required": True,
        },
    }
    write_json(root / EXECUTION_LOCK_PATH, lock)
    return lock


def load_approval_file(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return read_json(root / APPROVAL_TEMPLATE_PATH)


def approval_gate_status(root: Path) -> Dict[str, Any]:
    cleanup, cleanup_source = load_cleanup_report(root)
    plan, plan_source = load_archive_plan(root)
    freeze, freeze_source = read_json(root / FREEZE_PATH)
    conflict, conflict_source = read_json(root / PROTECTED_CONFLICT_PATH)

    candidates = archive_review_candidates(plan)
    template = build_approval_template(root, candidates)
    lock = build_execution_lock(root)

    blocked_candidates = []
    eligible_candidates = []
    for move in template["moves"]:
        if move.get("eligible_for_approval"):
            eligible_candidates.append(move)
        else:
            blocked_candidates.append(move)

    blockers: List[str] = []
    warnings: List[str] = []

    if cleanup_source.get("status") != "loaded":
        blockers.append("missing_v17_81_cleanup_report")
    if plan_source.get("status") != "loaded":
        blockers.append("missing_archive_plan_do_not_execute")
    if freeze_source.get("status") != "loaded":
        blockers.append("missing_v17_80_launch_candidate_freeze")
    if conflict_source.get("status") != "loaded":
        warnings.append("missing_protected_conflict_report")

    if not candidates:
        warnings.append("no_archive_review_candidates_found")
    if blocked_candidates:
        warnings.append(f"blocked_candidates_present:{len(blocked_candidates)}")

    status = "ARCHIVE_APPROVAL_READY_NO_EXECUTION"
    recommendation = "Review approved_archive_moves_template.json. Do not execute moves until explicit approval and post-move proof plan are ready."
    if blockers:
        status = "STOP"
        recommendation = "Do not prepare archive execution until cleanup proof, archive plan, and freeze files exist."

    gate = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": status,
        "recommendation": recommendation,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "sources": {
            "cleanup_report": cleanup_source,
            "archive_plan": plan_source,
            "launch_candidate_freeze": freeze_source,
            "protected_conflict_report": conflict_source,
        },
        "candidate_counts": {
            "archive_review_candidates": len(candidates),
            "eligible_for_approval": len(eligible_candidates),
            "blocked_from_approval": len(blocked_candidates),
        },
        "approval_template": str(APPROVAL_TEMPLATE_PATH).replace("\\", "/"),
        "execution_lock": lock,
        "execution_enabled_now": False,
        "delete_allowed": False,
        "archive_execution_allowed_by_installer": False,
        "required_post_archive_proofs": REQUIRED_POST_ARCHIVE_PROOFS,
    }

    write_json(root / GATE_PATH, gate)
    write_json(root / STOP_GO_PATH, {
        "version": VERSION,
        "generated_at": gate["generated_at"],
        "status": gate["status"],
        "blockers": gate["blockers"],
        "warnings": gate["warnings"],
        "recommendation": gate["recommendation"],
    })

    return gate


def approved_moves_from_file(root: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    approval, source = load_approval_file(root)
    if source.get("status") != "loaded":
        return [], {"source": source, "status": "blocked", "reason": "approval_file_missing"}

    if approval.get("operator_confirm_text") != APPROVAL_PHRASE:
        return [], {"source": source, "status": "blocked", "reason": "operator_confirm_text_missing_or_wrong"}

    raw = approval.get("moves")
    if not isinstance(raw, list):
        return [], {"source": source, "status": "blocked", "reason": "moves_not_list"}

    approved = []
    blocked = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if item.get("approved") is not True:
            continue
        p = normalize_path(str(item.get("path", "")))
        forbidden, reasons = is_forbidden_path(p)
        if forbidden:
            blocked.append({"path": p, "reasons": reasons})
        else:
            approved.append({"path": p, "operator_notes": item.get("operator_notes", "")})

    if blocked:
        return [], {"source": source, "status": "blocked", "reason": "approved_moves_include_forbidden_paths", "blocked": blocked}

    return approved, {"source": source, "status": "approved", "approved_count": len(approved)}


def execute_approved_archive_moves(project_root: Optional[Path | str] = None, confirm_text: str = "") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    gate = approval_gate_status(root)

    if confirm_text != APPROVAL_PHRASE:
        report = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "confirm_text_missing_or_wrong",
            "required_confirm_text": APPROVAL_PHRASE,
            "moves": [],
            "post_archive_proofs_required": REQUIRED_POST_ARCHIVE_PROOFS,
        }
        write_json(root / EXECUTION_REPORT_PATH, report)
        return report

    approved, approval_status = approved_moves_from_file(root)
    if approval_status.get("status") != "approved":
        report = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": approval_status.get("reason"),
            "approval_status": approval_status,
            "moves": [],
            "post_archive_proofs_required": REQUIRED_POST_ARCHIVE_PROOFS,
        }
        write_json(root / EXECUTION_REPORT_PATH, report)
        return report

    moved: List[Dict[str, Any]] = []
    blocked: List[Dict[str, Any]] = []

    for item in approved:
        source_rel = normalize_path(item["path"])
        source = root / source_rel
        if not source.exists():
            blocked.append({"path": source_rel, "reason": "source_missing"})
            continue

        forbidden, reasons = is_forbidden_path(source_rel)
        if forbidden:
            blocked.append({"path": source_rel, "reason": "forbidden_path", "details": reasons})
            continue

        destination = root / ARCHIVE_ROOT / source_rel
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            blocked.append({"path": source_rel, "reason": "destination_already_exists", "destination": rel(root, destination)})
            continue

        shutil.move(str(source), str(destination))
        moved.append({
            "source": source_rel,
            "destination": rel(root, destination),
            "operator_notes": item.get("operator_notes", ""),
        })

    status = "executed_with_blockers" if blocked and moved else "blocked" if blocked and not moved else "executed"
    report = {
        "version": VERSION,
        "generated_at": now(),
        "status": status,
        "executed": bool(moved),
        "moved": moved,
        "blocked": blocked,
        "post_archive_proofs_required": REQUIRED_POST_ARCHIVE_PROOFS,
        "delete_performed": False,
        "archive_root": str(ARCHIVE_ROOT).replace("\\", "/"),
    }
    write_json(root / EXECUTION_REPORT_PATH, report)
    return report


def write_markdown(root: Path, gate: Dict[str, Any]) -> None:
    lines = [
        "# Claire v17.82 Archive Approval Gate",
        "",
        f"Generated: {gate['generated_at']}",
        "",
        f"Status: **{gate['status']}**",
        "",
        f"Recommendation: {gate['recommendation']}",
        "",
        "## Hard Rule",
        "",
        "**This installer does not move or delete anything.**",
        "",
        "Archive movement requires editing `data/cleanup/approved_archive_moves_template.json` and explicit confirmation text.",
        "",
        "## Approval file",
        "",
        "`data/cleanup/approved_archive_moves_template.json`",
        "",
        "Required confirm text:",
        "",
        f"`{APPROVAL_PHRASE}`",
        "",
        "## Candidate counts",
        "",
    ]
    for key, value in gate.get("candidate_counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Required proof after any archive movement",
        "",
    ])
    for command in REQUIRED_POST_ARCHIVE_PROOFS:
        lines.append(f"- `{command}`")
    if gate.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        for warning in gate["warnings"]:
            lines.append(f"- {warning}")
    if gate.get("blockers"):
        lines.extend(["", "## Blockers", ""])
        for blocker in gate["blockers"]:
            lines.append(f"- {blocker}")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))
    write_text(root / REVIEW_MD_PATH, "\n".join(lines))


def build_archive_approval_gate(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    gate = approval_gate_status(root)
    write_markdown(root, gate)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": gate["generated_at"],
        "status": gate["status"],
        "recommendation": gate["recommendation"],
        "candidate_counts": gate["candidate_counts"],
        "approval_template": gate["approval_template"],
        "execution_enabled_now": False,
        "delete_allowed": False,
        "archive_execution_allowed_by_installer": False,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)
    return gate


def archive_approval_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    gate = build_archive_approval_gate(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": gate.get("status"),
        "recommendation": gate.get("recommendation"),
        "candidate_counts": gate.get("candidate_counts"),
        "approval_template": gate.get("approval_template"),
        "delete_allowed": False,
        "archive_execution_allowed_by_installer": False,
        "execution_enabled_now": False,
    }
