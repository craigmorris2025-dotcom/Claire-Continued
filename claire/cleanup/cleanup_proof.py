
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.81"
CONTRACT_NAME = "Cleanup Proof Before Archive/Delete"

REPORT_PATH = Path("data/cleanup/cleanup_proof_before_archive_delete.json")
ARCHIVE_PLAN_PATH = Path("data/cleanup/archive_plan_do_not_execute.json")
CONFLICT_PATH = Path("data/cleanup/protected_path_conflict_report.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/cleanup_proof_payload.json")
STOP_GO_PATH = Path("data/cleanup/v17_81_cleanup_stop_go.json")
STOP_GO_MD_PATH = Path("data/cleanup/v17_81_cleanup_stop_go.md")
REVIEW_MD_PATH = Path("data/cleanup/CLEANUP_REVIEW_ONLY.md")

PROTECTED_MANIFEST_PATH = Path("data/launch_candidate/protected_paths_manifest.json")
FREEZE_PATH = Path("data/launch_candidate/v17_80_launch_candidate_freeze.json")
CLEANUP_CANDIDATE_SOURCES = [
    Path("cleanup_candidates_do_not_delete_yet.json"),
    Path("cleanup_candidates_do_not_delete_yet.txt"),
    Path("data/cleanup/cleanup_candidates_do_not_delete_yet.json"),
    Path("data/cleanup/cleanup_candidates_do_not_delete_yet.txt"),
]

ALWAYS_REVIEW_ONLY = [
    "backend",
    "src",
    "claire live",
    "frontend/command_center/modern",
    "data",
    "docs",
    "tests",
    "requirements",
    ".github",
]

NEVER_DELETE_PATTERNS = [
    "claire/app.py",
    "claire/api",
    "frontend/command_center/modern/index.html",
    "LAUNCH_CLAIRE.bat",
    "START_CLAIRE_SAFE.bat",
    "VERIFY_CLAIRE_STARTUP.bat",
    "data/runtime/runtime_truth_canonical.json",
    "data/dashboard/operator_dashboard_state.json",
]

REFERENCE_SCAN_EXTENSIONS = {".py", ".html", ".js", ".css", ".bat", ".md", ".txt", ".json", ".toml", ".ini"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_path(value: str) -> str:
    return str(value or "").replace("\\", "/").strip().strip("./")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_json(path: Path) -> Tuple[Dict[str, object], Dict[str, object]]:
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


def path_info(root: Path, relative: str) -> Dict[str, object]:
    relative = normalize_path(relative)
    path = root / relative
    info: Dict[str, object] = {
        "path": relative,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }
    if path.exists() and path.is_file():
        info["size_bytes"] = path.stat().st_size
    if path.exists() and path.is_dir():
        files = [p for p in path.rglob("*") if p.is_file()]
        info["file_count"] = len(files)
        info["total_size_bytes_limited"] = sum(p.stat().st_size for p in files[:5000])
        info["count_limited"] = len(files) > 5000
    return info


def protected_paths(root: Path) -> Dict[str, object]:
    manifest, source = read_json(root / PROTECTED_MANIFEST_PATH)
    protected = []
    raw = manifest.get("protected_paths")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and item.get("path"):
                protected.append(normalize_path(str(item["path"])))
            elif isinstance(item, str):
                protected.append(normalize_path(item))
    for item in NEVER_DELETE_PATTERNS:
        if item not in protected:
            protected.append(item)
    return {"source": source, "paths": sorted(set(protected))}


def load_candidate_sources(root: Path) -> Dict[str, object]:
    loaded: List[Dict[str, object]] = []
    candidates: List[str] = []

    for rel_path in CLEANUP_CANDIDATE_SOURCES:
        path = root / rel_path
        if not path.exists():
            loaded.append({"path": str(rel_path).replace("\\", "/"), "status": "missing"})
            continue

        if path.suffix.lower() == ".json":
            payload, source = read_json(path)
            loaded.append(source)
            if isinstance(payload.get("candidates"), list):
                for item in payload["candidates"]:
                    if isinstance(item, dict) and item.get("path"):
                        candidates.append(normalize_path(str(item["path"])))
                    elif isinstance(item, str):
                        candidates.append(normalize_path(item))
            else:
                for key, value in payload.items():
                    if isinstance(value, dict) and value.get("path"):
                        candidates.append(normalize_path(str(value["path"])))
                    elif isinstance(value, list):
                        for sub in value:
                            if isinstance(sub, dict) and sub.get("path"):
                                candidates.append(normalize_path(str(sub["path"])))
                            elif isinstance(sub, str):
                                maybe = normalize_path(sub)
                                if "/" in maybe or "\\" in sub:
                                    candidates.append(maybe)
        else:
            loaded.append({"path": str(rel_path).replace("\\", "/"), "status": "loaded"})
            text = path.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                match = re.search(r"([A-Za-z0-9_. -]+(?:/|\\)[A-Za-z0-9_./\\ -]+|backend|src|claire live)", line)
                if match:
                    candidates.append(normalize_path(match.group(1)))

    seed_paths = [
        "backend",
        "src",
        "claire live",
        "quarantine_legacy_placeholders",
        "frontend/internet_operations_dashboard",
        "frontend/command_center/modern/internet_operations_dashboard.html",
        "frontend/command_center/modern/claire_single_screen_operator.js",
        "frontend/command_center/modern/claire_single_screen_operator.css",
        "frontend/command_center/modern/claire_functional_operator_dashboard.js",
        "frontend/command_center/modern/claire_functional_operator_dashboard.css",
        "frontend/command_center/modern/claire_connected_operator_dashboard.js",
        "frontend/command_center/modern/claire_connected_operator_dashboard.css",
    ]
    candidates.extend(seed_paths)

    unique = []
    seen = set()
    for item in candidates:
        item = normalize_path(item)
        if item and item not in seen:
            seen.add(item)
            unique.append(item)

    return {"sources": loaded, "candidates": unique}


def scan_references(root: Path, candidate: str, max_hits: int = 12) -> Dict[str, object]:
    candidate = normalize_path(candidate)
    basename = Path(candidate).name
    search_terms = sorted(set([candidate, candidate.replace("/", "\\"), basename]))
    hits: List[Dict[str, object]] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".venv" in path.parts or ".git" in path.parts or "backups" in path.parts:
            continue
        if path.suffix.lower() not in REFERENCE_SCAN_EXTENSIONS:
            continue
        rel_path = rel(root, path)
        if rel_path == candidate or rel_path.startswith(candidate.rstrip("/") + "/"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lower = text.lower()
        matched = [term for term in search_terms if term and term.lower() in lower]
        if matched:
            hits.append({"file": rel_path, "matched_terms": matched[:5]})
            if len(hits) >= max_hits:
                break

    return {"hit_count": len(hits), "hits": hits}


def overlaps_protected(candidate: str, protected: List[str]) -> Dict[str, object]:
    candidate = normalize_path(candidate).rstrip("/")
    conflicts = []
    for item in protected:
        p = normalize_path(item).rstrip("/")
        if not p:
            continue
        if candidate == p or candidate.startswith(p + "/") or p.startswith(candidate + "/"):
            conflicts.append(p)
    return {"has_conflict": bool(conflicts), "conflicts": sorted(set(conflicts))}


def classify_candidate(root: Path, candidate: str, protected: List[str]) -> Dict[str, object]:
    candidate = normalize_path(candidate)
    info = path_info(root, candidate)
    conflict = overlaps_protected(candidate, protected)
    refs = scan_references(root, candidate)

    review_only_reason: List[str] = []
    status = "unknown"

    if not info["exists"]:
        status = "not_found"
        review_only_reason.append("path_not_found")
    elif conflict["has_conflict"]:
        status = "blocked_protected_path"
        review_only_reason.append("overlaps_launch_candidate_protected_path")
    elif candidate in ALWAYS_REVIEW_ONLY or any(candidate.startswith(p.rstrip("/") + "/") for p in ALWAYS_REVIEW_ONLY):
        status = "review_only"
        review_only_reason.append("always_review_only_path")
    elif refs["hit_count"]:
        status = "review_only"
        review_only_reason.append("references_found")
    else:
        status = "candidate_for_archive_review"
        review_only_reason.append("no_protection_or_reference_conflict_found")

    if candidate == "backend":
        status = "review_only"
        review_only_reason.append("backend_folder_locked_until_manual_import_and_runtime_proof")

    return {
        "path": candidate,
        "classification": status,
        "reason": sorted(set(review_only_reason)),
        "path_info": info,
        "protected_conflict": conflict,
        "reference_scan": refs,
        "delete_allowed": False,
        "archive_allowed_now": False,
        "operator_review_required": True,
    }


def build_archive_plan(candidates: List[Dict[str, object]]) -> Dict[str, object]:
    review_candidates = [
        item for item in candidates
        if item.get("classification") == "candidate_for_archive_review"
    ]
    blocked = [
        item for item in candidates
        if item.get("classification") in {"blocked_protected_path", "review_only"}
    ]
    plan = {
        "version": VERSION,
        "generated_at": now(),
        "plan_type": "review_only_archive_plan_do_not_execute",
        "delete_allowed": False,
        "archive_execution_allowed": False,
        "operator_review_required": True,
        "candidate_for_archive_review_count": len(review_candidates),
        "blocked_or_review_only_count": len(blocked),
        "archive_review_candidates": review_candidates,
        "blocked_or_review_only": blocked,
        "recommended_archive_root": "archive_review_pending/v17_81/",
        "required_before_execution": [
            "Manual review each candidate",
            "Run endpoint smoke proof after any archive movement",
            "Run desktop startup proof after any archive movement",
            "Confirm dashboard bridge still works",
            "Confirm runtime truth and search command layer still work",
        ],
    }
    return plan


def determine_stop_go(classified: List[Dict[str, object]], freeze: Dict[str, object], protected: Dict[str, object]) -> Dict[str, object]:
    blockers: List[str] = []
    warnings: List[str] = []

    if freeze.get("source", {}).get("status") != "loaded":
        blockers.append("missing_v17_80_launch_candidate_freeze")

    if protected.get("source", {}).get("status") != "loaded":
        blockers.append("missing_protected_paths_manifest")

    protected_conflicts = [item["path"] for item in classified if item.get("classification") == "blocked_protected_path"]
    review_only = [item["path"] for item in classified if item.get("classification") == "review_only"]
    archive_review = [item["path"] for item in classified if item.get("classification") == "candidate_for_archive_review"]

    if protected_conflicts:
        warnings.append(f"protected_conflicts_present:{len(protected_conflicts)}")
    if review_only:
        warnings.append(f"review_only_paths_present:{len(review_only)}")
    if archive_review:
        warnings.append(f"archive_review_candidates_present:{len(archive_review)}")

    status = "CLEANUP_REVIEW_READY_NO_DELETE"
    recommendation = "Review archive candidates manually. Do not delete anything. Archive only after manual approval and another endpoint/startup proof pass."

    if blockers:
        status = "STOP"
        recommendation = "Do not proceed with cleanup review until freeze/protected manifest exists."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "protected_conflict_count": len(protected_conflicts),
        "review_only_count": len(review_only),
        "archive_review_candidate_count": len(archive_review),
        "recommendation": recommendation,
    }


def write_markdown(root: Path, report: Dict[str, object]) -> None:
    sg = report["stop_go"]
    lines = [
        "# Claire v17.81 Cleanup Proof Before Archive/Delete",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Hard Rule",
        "",
        "**This build does not delete anything. This build does not archive anything.**",
        "",
        "Cleanup is review-only until a follow-up approved archive build and proof pass.",
        "",
        "## Summary",
        "",
        f"- Protected conflicts: {sg['protected_conflict_count']}",
        f"- Review-only paths: {sg['review_only_count']}",
        f"- Archive review candidates: {sg['archive_review_candidate_count']}",
        "",
        "## Candidate Classifications",
        "",
    ]
    for item in report.get("classified_candidates", []):
        lines.append(f"- **{item.get('classification')}** `{item.get('path')}`")
        lines.append(f"  - Reason: {', '.join(item.get('reason', []))}")
        refs = item.get("reference_scan", {})
        if refs.get("hit_count"):
            lines.append(f"  - References found: {refs.get('hit_count')}")
    lines.extend([
        "",
        "## Next Safe Step",
        "",
        "Run manual review. Only then create a separate archive-only installer that moves approved candidates into an archive folder, followed immediately by endpoint smoke proof and startup proof.",
        "",
    ])
    if sg["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for warning in sg["warnings"]:
            lines.append(f"- {warning}")
    if sg["blockers"]:
        lines.append("")
        lines.append("## Blockers")
        lines.append("")
        for blocker in sg["blockers"]:
            lines.append(f"- {blocker}")
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))
    write_text(root / REVIEW_MD_PATH, "\n".join(lines))


def build_cleanup_proof(project_root: Optional[Path | str] = None) -> Dict[str, object]:
    root = Path(project_root or Path.cwd()).resolve()

    freeze_payload, freeze_source = read_json(root / FREEZE_PATH)
    freeze = {"source": freeze_source, "status": freeze_payload.get("status", "missing")}
    protected = protected_paths(root)
    candidate_data = load_candidate_sources(root)

    protected_list = list(protected.get("paths", []))
    classified = [
        classify_candidate(root, candidate, protected_list)
        for candidate in candidate_data["candidates"]
    ]

    archive_plan = build_archive_plan(classified)
    stop_go = determine_stop_go(classified, freeze, protected)

    conflict_report = {
        "version": VERSION,
        "generated_at": now(),
        "protected_source": protected.get("source"),
        "protected_paths": protected_list,
        "conflicts": [
            {
                "path": item["path"],
                "classification": item["classification"],
                "conflicts": item.get("protected_conflict", {}).get("conflicts", []),
            }
            for item in classified
            if item.get("protected_conflict", {}).get("has_conflict")
        ],
    }

    report = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "freeze": freeze,
        "candidate_sources": candidate_data["sources"],
        "candidate_count": len(classified),
        "classified_candidates": classified,
        "archive_plan_path": str(ARCHIVE_PLAN_PATH).replace("\\", "/"),
        "protected_conflict_report_path": str(CONFLICT_PATH).replace("\\", "/"),
        "rules": {
            "delete_allowed": False,
            "archive_execution_allowed": False,
            "operator_review_required": True,
            "endpoint_smoke_required_after_archive": True,
            "desktop_startup_required_after_archive": True,
            "backend_folder_delete_allowed": False,
            "protected_paths_must_not_be_moved": True,
        },
        "next": [
            "Manual review cleanup classifications",
            "v17.82 Archive-Only Move Plan if approved",
            "Run endpoint smoke proof after any archive movement",
            "Run desktop startup proof after any archive movement",
        ],
    }

    write_json(root / REPORT_PATH, report)
    write_json(root / ARCHIVE_PLAN_PATH, archive_plan)
    write_json(root / CONFLICT_PATH, conflict_report)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": report["generated_at"], **stop_go})
    write_markdown(root, report)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": report["generated_at"],
        "status": stop_go["status"],
        "recommendation": stop_go["recommendation"],
        "candidate_count": len(classified),
        "protected_conflict_count": stop_go["protected_conflict_count"],
        "review_only_count": stop_go["review_only_count"],
        "archive_review_candidate_count": stop_go["archive_review_candidate_count"],
        "delete_allowed": False,
        "archive_execution_allowed": False,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return report


def cleanup_proof_summary(project_root: Optional[Path | str] = None) -> Dict[str, object]:
    report = build_cleanup_proof(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": report.get("status"),
        "recommendation": report.get("stop_go", {}).get("recommendation"),
        "candidate_count": report.get("candidate_count"),
        "delete_allowed": False,
        "archive_execution_allowed": False,
        "archive_plan_path": report.get("archive_plan_path"),
        "protected_conflict_report_path": report.get("protected_conflict_report_path"),
    }
