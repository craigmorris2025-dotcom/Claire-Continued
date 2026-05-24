from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from claire.api.endpoint_reconciliation_report import RECONCILED_ALIASES

CANONICAL_FRONTEND_FILES = {
    "frontend/command_center/modern/claire_dashboard.html",
    "frontend/command_center/modern/claire_dashboard.js",
    "frontend/command_center/modern/index.html",
    "frontend/command_center/modern/dashboard_operator_console_contract.js",
}

LEGACY_FRONTEND_PREFIXES = (
    "frontend/export_dashboard/",
    "frontend/cockpit/",
    "frontend/discover/",
    "frontend/js/",
    "frontend/monitor/",
    "frontend/operator_dashboard/",
    "frontend/unified/",
    "frontend/command_center/modern/assets/",
)

LEGACY_FRONTEND_FILES = {
    "frontend/claire_dashboard_actions.js",
    "frontend/command_center/modern/claire_operating_environment.js",
    "frontend/command_center/modern/claire_single_screen_operator.js",
    "frontend/command_center/modern/dashboard_primary_web_search_binding.js",
    "frontend/command_center/modern/governed_provider_probe_ui_binding.js",
    "frontend/command_center/modern/governed_live_search_ui_binding.js",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_path(endpoint: str) -> str:
    return urlsplit(endpoint).path or endpoint


def template_matches(frontend_path: str, backend_path: str) -> bool:
    frontend_parts = frontend_path.strip("/").split("/")
    backend_parts = backend_path.strip("/").split("/")
    if len(frontend_parts) != len(backend_parts):
        return False
    for frontend_part, backend_part in zip(frontend_parts, backend_parts):
        if backend_part.startswith("{") and backend_part.endswith("}"):
            continue
        if frontend_part != backend_part:
            return False
    return True


def find_backend_match(endpoint: str, active_paths: set[str]) -> str | None:
    normalized = canonical_path(endpoint)
    if normalized in active_paths:
        return normalized
    for active_path in sorted(active_paths):
        if "{" in active_path and template_matches(normalized, active_path):
            return active_path
    return None


def owner_scope(owner_files: list[str]) -> str:
    if any(owner in CANONICAL_FRONTEND_FILES for owner in owner_files):
        return "canonical_dashboard"
    if all(
        owner in LEGACY_FRONTEND_FILES or owner.startswith(LEGACY_FRONTEND_PREFIXES)
        for owner in owner_files
    ):
        return "legacy_frontend_surface"
    return "mixed_or_unknown"


def classify_endpoint(
    endpoint: str,
    active_paths: set[str],
    frontend_paths: set[str],
    owner_files: list[str],
) -> tuple[str, str | None, str]:
    scope = owner_scope(owner_files)
    normalized = canonical_path(endpoint)
    if endpoint in RECONCILED_ALIASES:
        target = RECONCILED_ALIASES[endpoint]
        if find_backend_match(target, active_paths):
            return "stale_alias", target, "compatibility alias forwards to canonical backend owner"
        return "missing", target, "alias target is not mounted in active endpoint baseline"
    match = find_backend_match(endpoint, active_paths)
    if match:
        duplicate_aliases = [
            alias for alias, target in RECONCILED_ALIASES.items() if target == normalized and alias in frontend_paths
        ]
        if duplicate_aliases:
            return "duplicate", match, "canonical endpoint is active but stale aliases also remain in frontend"
        return "active", match, "frontend path directly matches active backend endpoint"
    if endpoint.startswith(("/api/cockpit/operator-experience/assets/", "/assets/")):
        return "remove", None, "static/legacy asset path should be removed or replaced by bundled dashboard assets"
    if scope == "legacy_frontend_surface":
        return "remove", None, "inactive/legacy frontend surface; not loaded by canonical dashboard"
    return "missing", None, "no active backend endpoint or approved compatibility alias found"


def build_table(active_endpoint_file: Path, frontend_map_file: Path) -> dict:
    active_payload = load_json(active_endpoint_file)
    frontend_payload = load_json(frontend_map_file)
    active_paths = {item["path"] for item in active_payload.get("endpoints", []) if item.get("path")}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for call in frontend_payload.get("calls", []):
        endpoint = call.get("frontend_path")
        if endpoint:
            grouped[str(endpoint)].append(call)
    frontend_paths = set(grouped)
    rows = []
    for endpoint in sorted(grouped):
        owner_files = sorted({str(call.get("file")) for call in grouped[endpoint] if call.get("file")})
        status, alias_target, notes = classify_endpoint(endpoint, active_paths, frontend_paths, owner_files)
        rows.append(
            {
                "frontend_path": endpoint,
                "backend_match": find_backend_match(endpoint, active_paths) is not None,
                "status": status,
                "alias_target": alias_target,
                "owner_file": ", ".join(owner_files[:5]),
                "owner_file_count": len(owner_files),
                "caller_count": len(grouped[endpoint]),
                "notes": notes,
            }
        )
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["status"]] += 1
    return {
        "schema_version": "claire.endpoint_reconciliation_lock.v1",
        "active_endpoint_file": active_endpoint_file.as_posix(),
        "frontend_map_file": frontend_map_file.as_posix(),
        "active_route_count": active_payload.get("route_count"),
        "unique_frontend_endpoint_count": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "rows": rows,
    }


def write_reports(payload: dict, report_date: str, reports_dir: Path) -> dict[str, object]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = reports_dir / f"endpoint_reconciliation_{report_date}.json"
    md_path = reports_dir / f"endpoint_reconciliation_{report_date}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Endpoint Reconciliation",
        f"Generated: {report_date}",
        "",
        f"Active route count: `{payload['active_route_count']}`",
        f"Unique frontend endpoints: `{payload['unique_frontend_endpoint_count']}`",
        f"Status counts: `{payload['status_counts']}`",
        "",
        "| frontend_path | backend_match | status | alias_target | owner_file | notes |",
        "|---|---:|---|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| `{frontend_path}` | {backend_match} | `{status}` | {alias_target} | {owner_file} | {notes} |".format(
                frontend_path=row["frontend_path"],
                backend_match="yes" if row["backend_match"] else "no",
                status=row["status"],
                alias_target=f"`{row['alias_target']}`" if row["alias_target"] else "",
                owner_file="<br>".join(f"`{item.strip()}`" for item in row["owner_file"].split(", ") if item.strip()),
                notes=row["notes"],
            )
        )
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path), "status_counts": payload["status_counts"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--active-endpoints", default="reports/backend_baseline_20260524_ACTIVE_ENDPOINTS.json")
    parser.add_argument("--frontend-map", default="reports/frontend_fetch_map_20260524.json")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--date", default="20260524")
    args = parser.parse_args()
    payload = build_table(Path(args.active_endpoints), Path(args.frontend_map))
    print(json.dumps(write_reports(payload, args.date, Path(args.reports_dir)), indent=2))


if __name__ == "__main__":
    main()
