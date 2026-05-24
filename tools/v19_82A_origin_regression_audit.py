from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


VERSION = "v19.82A.1"
BUILD_NAME = "Origin Regression Audit Regex Repair"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def safe_rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def scan_files(root: Path, patterns: list[str], max_files: int = 20000) -> list[Path]:
    files: list[Path] = []
    skip_parts = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", "site-packages", "dist", "build"}
    for pattern in patterns:
        for path in root.rglob(pattern):
            if len(files) >= max_files:
                return files
            if any(part in skip_parts for part in path.parts):
                continue
            if path.is_file():
                files.append(path)
    seen = set()
    out = []
    for f in files:
        key = str(f)
        if key not in seen:
            seen.add(key)
            out.append(f)
    return out


def find_matches(root: Path, files: list[Path], terms: list[str]) -> list[dict]:
    matches = []
    for path in files:
        text = read_text(path)
        if not text:
            continue
        lowered = text.lower()
        for term in terms:
            count = lowered.count(term.lower())
            if count:
                matches.append({"file": safe_rel(root, path), "term": term, "count": count})
    return matches


def extract_quoted_path(line: str) -> str | None:
    # Simple safe parser: find first quoted string that starts with /
    for quote in ['"', "'"]:
        parts = line.split(quote)
        for i in range(1, len(parts), 2):
            candidate = parts[i].strip()
            if candidate.startswith("/"):
                return candidate
    return None


def extract_routes(root: Path, files: list[Path]) -> list[dict]:
    routes = []
    methods = [".get(", ".post(", ".put(", ".delete(", ".patch("]
    for path in files:
        text = read_text(path)
        if not text:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            lower = stripped.lower()
            is_route_line = (
                stripped.startswith("@router.") or
                stripped.startswith("@app.") or
                "add_api_route(" in stripped
            )
            if not is_route_line:
                continue
            endpoint = extract_quoted_path(stripped)
            method = None
            for item in methods:
                if item in lower:
                    method = item.strip(".(").upper()
                    break
            if endpoint:
                routes.append({
                    "file": safe_rel(root, path),
                    "line": lineno,
                    "endpoint": endpoint,
                    "method": method,
                    "match": stripped[:240],
                })
    return routes


def build_endpoint_conflicts(routes: list[dict]) -> dict:
    by_path = {}
    for route in routes:
        endpoint = route.get("endpoint")
        if endpoint:
            by_path.setdefault(endpoint, []).append({
                "method": route.get("method"),
                "file": route["file"],
                "line": route.get("line"),
                "match": route["match"],
            })
    conflicts = {path: refs for path, refs in by_path.items() if len({r["file"] for r in refs}) > 1}
    return {
        "route_count": len(by_path),
        "duplicate_or_multi_file_routes": conflicts,
        "payload_routes_present": {
            "/dashboard/payload": "/dashboard/payload" in by_path,
            "/dashboard/payload/status": "/dashboard/payload/status" in by_path,
        },
        "run_contract_routes_present": {
            route: route in by_path for route in [
                "/runs/start",
                "/runs/{run_id}/status",
                "/runs/{run_id}/lifecycle",
                "/runs/{run_id}/gates",
                "/runs/{run_id}/missing-evidence",
                "/runs/{run_id}/enrich",
                "/universes",
                "/universes/{universe_id}",
                "/universes/{universe_id}/probe",
            ]
        },
    }


def run_audit(project_root: Path | None = None) -> dict:
    root = project_root or Path.cwd()
    audit_dir = root / "audits" / "v19_82A_origin_regression_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    files = scan_files(root, ["*.py", "*.js", "*.html", "*.css", "*.json", "*.md", "*.txt", "*.bat"])

    key_paths = {
        "version_json": root / "version.json",
        "main_py": root / "main.py",
        "launcher": root / "LAUNCH_PLATFORM.bat",
        "backend_app": root / "claire" / "app.py",
        "payload_bridge": root / "claire" / "api" / "dashboard_payload_bridge.py",
        "new_cockpit": root / "frontend" / "cockpit" / "shell" / "cockpit_shell.html",
        "old_dashboard": root / "frontend" / "command_center" / "modern" / "index.html",
        "endpoint_contract": root / "frontend" / "cockpit" / "shared" / "pipeline_endpoint_contract.json",
        "autonomous_contract": root / "frontend" / "cockpit" / "cockpit_autonomous_lifecycle_contract.json",
    }
    path_status = {name: path.exists() for name, path in key_paths.items()}

    legacy_terms = ["v5.", "v5.90", "v6.", "post-eval", "post_eval", "evaluation", "eval_score", "command_center", "frontend/command_center", "frontend\\command_center", "src/claire", "src\\claire", "aiohttp", "localhost:8765", "dashboard/alignment"]
    legacy_matches = find_matches(root, files, legacy_terms)

    scoring_terms = ["threshold", "score", "confidence", "post-eval", "post_eval", "evaluation", "breakthrough_threshold", "route_confidence", "source_trust", "buildability", "viability", "manufacturability", "feasibility", "acquirer_fit"]
    scoring_matches = find_matches(root, files, scoring_terms)

    dashboard_terms = ["command_center/modern", "command_center\\modern", "frontend/command_center", "frontend\\command_center", "cockpit_shell.html", "payload_adapter", "/dashboard/payload", "dashboard_payload_bridge", "route_workspace_renderer"]
    dashboard_matches = find_matches(root, files, dashboard_terms)

    routes = extract_routes(root, [f for f in files if f.suffix == ".py"])
    endpoint_conflicts = build_endpoint_conflicts(routes)

    launcher_text = read_text(key_paths["launcher"])
    launcher_report = {
        "exists": key_paths["launcher"].exists(),
        "mentions_new_cockpit": "frontend\\cockpit\\shell\\cockpit_shell.html" in launcher_text or "frontend/cockpit/shell/cockpit_shell.html" in launcher_text,
        "mentions_old_dashboard": "frontend\\command_center\\modern\\index.html" in launcher_text or "frontend/command_center/modern/index.html" in launcher_text,
        "uses_main_py": "python main.py" in launcher_text,
    }

    hard_blockers = []
    warnings = []
    if not path_status["backend_app"]:
        hard_blockers.append("Missing claire/app.py")
    if not path_status["main_py"]:
        hard_blockers.append("Missing main.py")
    if not path_status["launcher"]:
        hard_blockers.append("Missing LAUNCH_PLATFORM.bat")
    if not path_status["new_cockpit"]:
        hard_blockers.append("Missing new cockpit shell")
    if not path_status["payload_bridge"]:
        warnings.append("Missing dashboard_payload_bridge.py; payload route may be unavailable")
    if not launcher_report["mentions_new_cockpit"]:
        warnings.append("Launcher does not visibly target new cockpit shell")
    if not endpoint_conflicts["payload_routes_present"]["/dashboard/payload"]:
        warnings.append("Static route scan did not find /dashboard/payload")
    if endpoint_conflicts["duplicate_or_multi_file_routes"]:
        warnings.append("Duplicate or multi-file route definitions detected")

    reports = {
        "lineage_report.json": {
            "version": VERSION,
            "build_name": BUILD_NAME,
            "created_at": utc_now(),
            "file_count_scanned": len(files),
            "path_status": path_status,
            "launcher_report": launcher_report,
            "version_report": {"exists": key_paths["version_json"].exists(), "raw": read_text(key_paths["version_json"])[:1000]},
            "hard_blockers": hard_blockers,
            "warnings": warnings,
        },
        "legacy_dependency_report.json": {
            "version": VERSION,
            "created_at": utc_now(),
            "legacy_terms": legacy_terms,
            "matches": legacy_matches[:1000],
            "match_count": len(legacy_matches),
            "interpretation": "Matches are not automatically bad; they identify places where old assumptions may still influence current runtime.",
        },
        "scoring_origin_report.json": {
            "version": VERSION,
            "created_at": utc_now(),
            "matches": scoring_matches[:1000],
            "match_count": len(scoring_matches),
            "risk": "Old post-eval scoring must not govern autonomous route decisions unless migrated into route gate policy.",
        },
        "dashboard_regression_report.json": {
            "version": VERSION,
            "created_at": utc_now(),
            "matches": dashboard_matches[:1000],
            "match_count": len(dashboard_matches),
            "risk": "Old command_center references are acceptable only as fallback/reference, not primary cockpit truth ownership.",
            "launcher_report": launcher_report,
        },
        "endpoint_conflict_report.json": {"version": VERSION, "created_at": utc_now(), **endpoint_conflicts},
    }

    stop_go = {
        "version": VERSION,
        "created_at": utc_now(),
        "go": len(hard_blockers) == 0,
        "hard_blockers": hard_blockers,
        "warnings": warnings,
        "required_before_phase_a": [
            "Confirm launcher targets new cockpit.",
            "Confirm /dashboard/payload and /dashboard/payload/status are mounted or planned in Phase A.",
            "Confirm old post-eval scoring is migrated to route gate policy before autonomous routing.",
            "Confirm old dashboard remains fallback only.",
        ],
        "next_recommended_build": "v19.82B Regression Lock / Source-of-Truth Repair" if warnings else "v19.82-v19.87 Runtime / Source / Web Plateau",
    }
    reports["stop_go_report.json"] = stop_go

    for name, data in reports.items():
        (audit_dir / name).write_text(json.dumps(data, indent=2), encoding="utf-8")

    md_lines = [
        f"# Claire {VERSION} Origin-to-Current Build Lineage Audit",
        "",
        f"- Created: {stop_go['created_at']}",
        f"- Files scanned: {len(files)}",
        f"- GO: {stop_go['go']}",
        f"- Hard blockers: {len(hard_blockers)}",
        f"- Warnings: {len(warnings)}",
        "",
        "## Hard Blockers",
        "",
    ]
    md_lines.extend([f"- {item}" for item in hard_blockers] or ["- None"])
    md_lines.extend(["", "## Warnings", ""])
    md_lines.extend([f"- {item}" for item in warnings] or ["- None"])
    md_lines.extend(["", "## Next", "", stop_go["next_recommended_build"], ""])
    (audit_dir / "stop_go_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {"audit_dir": str(audit_dir), "stop_go": stop_go, "reports": list(reports.keys()) + ["stop_go_report.md"]}


if __name__ == "__main__":
    print(json.dumps(run_audit(), indent=2))
