from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_PATH = Path("data/endpoint_contracts/endpoint_reconciliation_report.json")


RECONCILED_ALIASES: dict[str, str] = {
    "/system/runtime-execution/summary": "/runtime/status",
    "/system/runtime-state/summary": "/runtime/state",
    "/system/runtime-propagation/summary": "/runtime/continuous/status",
    "/api/dashboard/search/provider/status": "/api/search/providers/status",
    "/api/evidence/governed/status": "/api/evidence/quarantine/status",
    "/api/evidence/governed/cards": "/api/evidence/quarantine/cards",
    "/api/evidence/governed/actions": "/api/evidence/quarantine/actions",
    "/api/search/readiness/preflight": "/api/search/readiness/audit",
    "/api/search/metadata/payload": "/api/search/metadata/adapter/payload",
    "/api/search/governed/plans": "/api/search/governed/query/payload",
    "/api/search/governed/actions": "/api/search/governed/query/actions",
    "/api/cockpit/search-results/payload": "/api/evidence/quarantine/payload",
    "/api/sources/gaps/payload": "/api/sources/policy/payload",
    "/api/internet/live-toggle/preflight": "/internet/live-probe/status",
    "/api/internet/provider/probe": "/operator/search/web/run-governed-probe",
    "/api/internet/fetch/controlled": "/internet/live-probe/run",
    "/api/internet/live-metadata/run": "/internet/live-probe/run",
    "/api/internet/proposals/review": "/api/update-governance/open-web/request",
    "/api/internet/proposals/export": "/api/update-governance/open-web/panel",
    "/api/command": "/api/cockpit/command/plan",
    "/api/health": "/health",
    "/api/update/check": "/api/update/status",
    "/api/update/prepare": "/api/platform/update/plan",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _route_paths(app: Any | None) -> set[str]:
    if app is None:
        return set()
    return {getattr(route, "path", "") for route in getattr(app, "routes", []) if getattr(route, "path", "")}


def _frontend_fetch_paths(root: Path) -> list[dict[str, Any]]:
    frontend = root / "frontend"
    if not frontend.exists():
        return []
    fetch_pattern = re.compile(r"fetch\(\s*['\"](/[^'\"`\\s)]*)['\"]")
    endpoint_pattern = re.compile(r"(?:endpoint|url|route|path|API|STATUS_URL|PAYLOAD_URL)\s*[:=]\s*['\"](/[^'\"`\\s)]*)['\"]")
    results: list[dict[str, Any]] = []
    for path in sorted(frontend.rglob("*.js")):
        if ".bak" in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matches = list(fetch_pattern.finditer(text)) + list(endpoint_pattern.finditer(text))
        for match in matches:
            endpoint = match.group(1).strip()
            if "{" in endpoint or "${" in endpoint:
                endpoint = endpoint.split("${", 1)[0]
            if endpoint in {"/", "/api/", "/system/", "/runtime/", "/dashboard/", "/operator/"}:
                continue
            if " " in endpoint:
                continue
            results.append(
                {
                    "file": str(path.relative_to(root)).replace("\\", "/"),
                    "endpoint": endpoint,
                }
            )
    return results


def build_endpoint_reconciliation_report(app: Any | None = None, project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    mounted = _route_paths(app)
    frontend_calls = _frontend_fetch_paths(root)
    reconciled: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for call in frontend_calls:
        endpoint = call["endpoint"]
        if endpoint in mounted:
            status = "active"
            canonical = endpoint
        elif endpoint in RECONCILED_ALIASES:
            status = "compatibility_alias"
            canonical = RECONCILED_ALIASES[endpoint]
        else:
            status = "unresolved"
            canonical = None
        row = {**call, "status": status, "canonical_endpoint": canonical}
        reconciled.append(row)
        if status == "unresolved":
            unresolved.append(row)

    payload = {
        "schema_version": "claire.endpoint_reconciliation_report.v1",
        "status": "clean" if not unresolved else "gaps_present",
        "generated_at": _now(),
        "frontend_call_count": len(frontend_calls),
        "mounted_route_count": len(mounted),
        "compatibility_alias_count": len(RECONCILED_ALIASES),
        "unresolved_count": len(unresolved),
        "aliases": RECONCILED_ALIASES,
        "unresolved": unresolved[:200],
        "frontend_calls": reconciled[:500],
        "next_rule": "Replace compatibility aliases with canonical frontend calls after dashboard stability is verified.",
    }
    out = root / REPORT_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
