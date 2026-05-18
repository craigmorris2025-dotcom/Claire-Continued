from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_VERSION = "v19.89.8-S1295-S1322-system-vs-dashboard-operation-gap-audit"


CAPABILITY_CATALOG: list[dict[str, Any]] = [
    {
        "key": "system_health_plateau",
        "label": "System health, plateau lock, and audit proof",
        "required_for_operation": True,
        "route_patterns": ["/health", "/api/audit/", "/dashboard/audit/"],
        "frontend_terms": ["plateau", "audit", "health", "system"],
        "button_terms": ["audit", "plateau", "health", "system"],
    },
    {
        "key": "dashboard_payload",
        "label": "Canonical dashboard payload and status",
        "required_for_operation": True,
        "route_patterns": ["/dashboard/payload", "/dashboard/payload/status"],
        "frontend_terms": ["/dashboard/payload", "dashboard payload", "payload status"],
        "button_terms": ["refresh", "payload", "status"],
    },
    {
        "key": "dashboard_actions",
        "label": "Dashboard action registry, summary, preview, and result",
        "required_for_operation": True,
        "route_patterns": ["/dashboard/actions/"],
        "frontend_terms": ["/dashboard/actions/", "action registry", "actions summary", "actions preview", "actions result"],
        "button_terms": ["action", "preview", "plan search", "governed search"],
    },
    {
        "key": "operator_console",
        "label": "Operator console controls and action result binding",
        "required_for_operation": True,
        "route_patterns": ["/dashboard/operator-console", "/api/dashboard/operator-console", "/dashboard/operator-action"],
        "frontend_terms": ["operator-console", "operator-action", "operator console", "operation"],
        "button_terms": ["operator", "operation", "plan", "review", "preview"],
    },
    {
        "key": "cockpit_operations",
        "label": "Cockpit operations, control surface, and visual operations",
        "required_for_operation": True,
        "route_patterns": ["/api/cockpit/operations", "/api/cockpit/control-surface", "/api/cockpit/operation-visuals", "/api/cockpit/operator-experience", "/api/cockpit/operational-proof"],
        "frontend_terms": ["cockpit/operations", "control-surface", "operation-visuals", "operator-experience", "operational-proof"],
        "button_terms": ["operations", "control", "experience", "visual", "proof"],
    },
    {
        "key": "command_bar",
        "label": "Command bar operation payload, buttons, and preview",
        "required_for_operation": True,
        "route_patterns": ["/api/command-bar/"],
        "frontend_terms": ["command-bar", "command bar"],
        "button_terms": ["command", "submit", "search", "run"],
    },
    {
        "key": "governed_search",
        "label": "Governed search planning and search result surfaces",
        "required_for_operation": True,
        "route_patterns": ["/api/search/governed", "/api/cockpit/search", "/api/dashboard/search", "/api/search/results"],
        "frontend_terms": ["search/governed", "cockpit/search", "dashboard/search", "search-results", "governed search"],
        "button_terms": ["search", "governed", "query", "results"],
    },
    {
        "key": "provider_readiness",
        "label": "Search provider readiness, configuration, manual probe, and stop gates",
        "required_for_operation": True,
        "route_patterns": ["/api/search/provider", "/api/search/providers", "/api/internet/provider"],
        "frontend_terms": ["search/provider", "search/providers", "provider", "manual-probe"],
        "button_terms": ["provider", "probe", "readiness", "configure"],
    },
    {
        "key": "metadata_live_probe",
        "label": "Metadata probe, controlled live probe, and governed web probe boundaries",
        "required_for_operation": True,
        "route_patterns": ["/api/search/metadata", "/api/governed/live-probe", "/api/governed-web/metadata-probe", "/api/internet/metadata"],
        "frontend_terms": ["metadata", "live-probe", "metadata-probe", "governed-web"],
        "button_terms": ["metadata", "probe", "live", "head"],
    },
    {
        "key": "evidence_review",
        "label": "Evidence quarantine, evidence cards, review, and promotion preview",
        "required_for_operation": True,
        "route_patterns": ["/api/evidence/", "/api/search/evidence/"],
        "frontend_terms": ["evidence", "quarantine", "promotion-preview", "review"],
        "button_terms": ["evidence", "review", "quarantine", "promote"],
    },
    {
        "key": "source_registry_policy",
        "label": "Source registry, source policy, gaps, intake, and live source catalog",
        "required_for_operation": True,
        "route_patterns": ["/api/sources/", "/api/feeds/live-source-catalog", "/api/evidence/source/intake"],
        "frontend_terms": ["sources", "source", "source-ingestion", "live-source-catalog", "gaps"],
        "button_terms": ["source", "sources", "policy", "gaps", "intake"],
    },
    {
        "key": "body_read_gates",
        "label": "Body-read authorization, extraction scope, sanitizer, manual gate, and stop gate",
        "required_for_operation": True,
        "route_patterns": ["/api/web/body-read", "/api/cockpit/body-read", "/api/internet/body-read"],
        "frontend_terms": ["body-read", "body read", "sanitizer", "extraction-scope", "manual-gate"],
        "button_terms": ["body", "read", "sanitize", "extract", "authorize"],
    },
    {
        "key": "runtime_spine_lifecycle",
        "label": "Runtime spine, evidence lifecycle, routing preview, and operator control",
        "required_for_operation": True,
        "route_patterns": ["/api/governed/runtime-spine", "/api/evidence/lifecycle"],
        "frontend_terms": ["runtime-spine", "evidence/lifecycle", "lifecycle", "routing"],
        "button_terms": ["runtime", "lifecycle", "routing", "spine"],
    },
    {
        "key": "update_truth_promotion",
        "label": "Update proposal, runtime truth promotion preview, and source ingestion draft",
        "required_for_operation": True,
        "route_patterns": ["/api/web/update-proposal", "/api/web/runtime-truth", "/api/web/source-ingestion"],
        "frontend_terms": ["update-proposal", "runtime-truth", "source-ingestion"],
        "button_terms": ["update", "truth", "promote", "ingest"],
    },
    {
        "key": "live_intelligence_catalog",
        "label": "Live intelligence status and live source catalog health",
        "required_for_operation": True,
        "route_patterns": ["/api/live-intelligence", "/api/feeds/live-source-catalog"],
        "frontend_terms": ["live-intelligence", "live-source-catalog", "live intelligence"],
        "button_terms": ["live", "catalog", "intelligence"],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="utf-8-sig")
        except Exception:
            return ""


def _strip_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value, flags=re.S)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _route_inventory() -> list[dict[str, Any]]:
    from claire.app import create_app

    app = create_app()
    routes: list[dict[str, Any]] = []
    for route in app.routes:
        path = str(getattr(route, "path", ""))
        methods = sorted(method for method in (getattr(route, "methods", set()) or set()) if method not in {"HEAD", "OPTIONS"})
        name = str(getattr(route, "name", ""))
        if not path:
            continue
        routes.append({"path": path, "methods": methods, "name": name})
    return routes


def _frontend_inventory(root: Path) -> dict[str, Any]:
    frontend_root = root / "frontend" / "command_center" / "modern"
    files: list[Path] = []
    if frontend_root.exists():
        for suffix in ("*.html", "*.js", "*.css"):
            files.extend(frontend_root.rglob(suffix))

    file_entries: list[dict[str, Any]] = []
    fetches: list[dict[str, str]] = []
    buttons: list[dict[str, str]] = []
    click_handlers: list[dict[str, str]] = []
    data_action_tokens: list[dict[str, str]] = []
    all_text_parts: list[str] = []

    fetch_patterns = [
        re.compile(r"fetch\(\s*['\"`]([^'\"`]+)['\"`]", re.I),
        re.compile(r"axios\.(?:get|post|put|patch|delete)\(\s*['\"`]([^'\"`]+)['\"`]", re.I),
    ]
    button_pattern = re.compile(r"<button\b([^>]*)>(.*?)</button>", re.I | re.S)
    data_attr_pattern = re.compile(r"data-(?:action-key|claire-action-key|operator-action|action|operation-key)=['\"`]([^'\"`]+)['\"`]", re.I)
    click_pattern = re.compile(r"(addEventListener\(\s*['\"`]click['\"`]|onclick\s*=|querySelector(?:All)?\([^)]*button)", re.I)

    for path in sorted(set(files)):
        rel = _rel(root, path)
        text = _read_text(path)
        all_text_parts.append(text)
        file_entries.append({"file": rel, "size": len(text)})

        for pattern in fetch_patterns:
            for match in pattern.finditer(text):
                fetches.append({"file": rel, "url": match.group(1)})

        for match in button_pattern.finditer(text):
            attrs = match.group(1)
            label = _strip_html(match.group(2))
            buttons.append({"file": rel, "label": label, "attrs": attrs.strip()[:500]})

        for match in data_attr_pattern.finditer(text):
            data_action_tokens.append({"file": rel, "token": match.group(1)})

        for match in click_pattern.finditer(text):
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 240)
            click_handlers.append({"file": rel, "snippet": text[start:end].replace("\n", " ")[:500]})

    all_text = "\n".join(all_text_parts)
    return {
        "frontend_root": _rel(root, frontend_root),
        "file_count": len(file_entries),
        "files": file_entries,
        "fetch_count": len(fetches),
        "fetches": fetches,
        "button_count": len(buttons),
        "buttons": buttons,
        "data_action_count": len(data_action_tokens),
        "data_action_tokens": data_action_tokens,
        "click_handler_count": len(click_handlers),
        "click_handlers": click_handlers,
        "all_text_lower": all_text.lower(),
    }


def _route_matches(route_path: str, patterns: list[str]) -> bool:
    route_lower = route_path.lower()
    return any(pattern.lower() in route_lower for pattern in patterns)


def _text_has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def _fetch_matches(fetch_url: str, patterns: list[str], terms: list[str]) -> bool:
    lower = fetch_url.lower()
    return any(pattern.lower() in lower for pattern in patterns) or any(term.lower() in lower for term in terms)


def _button_matches(button: dict[str, str], terms: list[str]) -> bool:
    haystack = _normalize((button.get("label") or "") + " " + (button.get("attrs") or ""))
    return any(_normalize(term) in haystack for term in terms if _normalize(term))


def _analyze_capabilities(routes: list[dict[str, Any]], frontend: dict[str, Any]) -> list[dict[str, Any]]:
    capabilities: list[dict[str, Any]] = []
    fetches = frontend.get("fetches", [])
    buttons = frontend.get("buttons", [])
    data_tokens = frontend.get("data_action_tokens", [])
    all_text = frontend.get("all_text_lower", "")

    for capability in CAPABILITY_CATALOG:
        patterns = capability["route_patterns"]
        frontend_terms = capability["frontend_terms"]
        button_terms = capability["button_terms"]

        backend_routes = [
            route
            for route in routes
            if _route_matches(route["path"], patterns)
        ]
        matching_fetches = [
            fetch
            for fetch in fetches
            if _fetch_matches(fetch["url"], patterns, frontend_terms)
        ]
        matching_buttons = [
            button
            for button in buttons
            if _button_matches(button, button_terms)
        ]
        matching_data_tokens = [
            token
            for token in data_tokens
            if _text_has_any(token.get("token", ""), button_terms + frontend_terms)
        ]

        frontend_mentions = _text_has_any(all_text, frontend_terms)

        backend_available = len(backend_routes) > 0
        frontend_fetch_bound = len(matching_fetches) > 0
        button_present = len(matching_buttons) > 0 or len(matching_data_tokens) > 0

        if backend_available and frontend_fetch_bound and button_present:
            status = "bound"
        elif backend_available and frontend_fetch_bound and not button_present:
            status = "fetch_only_no_visible_button"
        elif backend_available and not frontend_fetch_bound and button_present:
            status = "button_without_fetch_binding"
        elif backend_available and frontend_mentions and not frontend_fetch_bound:
            status = "mentioned_but_not_fetch_bound"
        elif backend_available:
            status = "backend_available_dashboard_missing"
        else:
            status = "backend_missing"

        capabilities.append(
            {
                "key": capability["key"],
                "label": capability["label"],
                "required_for_operation": capability["required_for_operation"],
                "status": status,
                "backend_available": backend_available,
                "frontend_fetch_bound": frontend_fetch_bound,
                "button_present": button_present,
                "frontend_mentions": frontend_mentions,
                "backend_route_count": len(backend_routes),
                "frontend_fetch_count": len(matching_fetches),
                "button_count": len(matching_buttons),
                "data_action_count": len(matching_data_tokens),
                "backend_routes": backend_routes[:80],
                "frontend_fetches": matching_fetches[:40],
                "buttons": matching_buttons[:40],
                "data_actions": matching_data_tokens[:40],
                "gap": None if status == "bound" else _gap_text(status),
            }
        )
    return capabilities


def _gap_text(status: str) -> str:
    return {
        "fetch_only_no_visible_button": "Backend is fetched but the dashboard does not expose an obvious user-facing control.",
        "button_without_fetch_binding": "Dashboard appears to have a control, but no matching backend fetch/result binding was found.",
        "mentioned_but_not_fetch_bound": "Dashboard mentions this capability, but no matching backend fetch binding was found.",
        "backend_available_dashboard_missing": "Backend capability exists, but the active dashboard has no clear fetch or button binding for it.",
        "backend_missing": "No backend route was found for this required capability.",
    }.get(status, "Unclassified gap.")


def _duplicate_route_report(routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter((route["path"], tuple(route["methods"])) for route in routes)
    duplicates: list[dict[str, Any]] = []
    for (path, methods), count in counts.items():
        if count > 1:
            names = [route["name"] for route in routes if route["path"] == path and tuple(route["methods"]) == methods]
            duplicates.append({"path": path, "methods": list(methods), "count": count, "names": names[:20]})
    return duplicates


def _route_domain_counts(routes: list[dict[str, Any]]) -> dict[str, int]:
    domains: dict[str, int] = defaultdict(int)
    for route in routes:
        parts = [part for part in route["path"].split("/") if part]
        if not parts:
            domains["root"] += 1
        elif parts[0] == "api" and len(parts) > 1:
            domains[f"/api/{parts[1]}"] += 1
        else:
            domains[f"/{parts[0]}"] += 1
    return dict(sorted(domains.items()))


def build_system_dashboard_gap_audit(root: Path | None = None, *, write_report: bool = True) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve()
    routes = _route_inventory()
    frontend = _frontend_inventory(root)
    capabilities = _analyze_capabilities(routes, frontend)

    required = [capability for capability in capabilities if capability["required_for_operation"]]
    bound = [capability for capability in required if capability["status"] == "bound"]
    lagging = [capability for capability in required if capability["status"] != "bound"]
    backend_available_dashboard_missing = [
        capability
        for capability in required
        if capability["status"] in {"backend_available_dashboard_missing", "mentioned_but_not_fetch_bound", "fetch_only_no_visible_button"}
    ]
    button_without_fetch = [
        capability
        for capability in required
        if capability["status"] == "button_without_fetch_binding"
    ]

    routes_by_method = Counter()
    for route in routes:
        for method in route["methods"]:
            routes_by_method[method] += 1

    report: dict[str, Any] = {
        "audit_version": AUDIT_VERSION,
        "generated_at": _utc_now(),
        "root": str(root),
        "summary": {
            "backend_route_count": len(routes),
            "backend_get_route_count": routes_by_method.get("GET", 0),
            "backend_post_route_count": routes_by_method.get("POST", 0),
            "frontend_file_count": frontend["file_count"],
            "frontend_fetch_count": frontend["fetch_count"],
            "frontend_button_count": frontend["button_count"],
            "frontend_click_handler_count": frontend["click_handler_count"],
            "capability_count": len(capabilities),
            "required_capability_count": len(required),
            "bound_required_capability_count": len(bound),
            "lagging_required_capability_count": len(lagging),
            "dashboard_operational_binding_score": round((len(bound) / len(required)) * 100, 2) if required else 0,
            "system_has_operational_backend": len(routes) > 100 and any(route["path"] == "/dashboard/actions/registry" for route in routes),
            "dashboard_lagging_backend": len(lagging) > 0,
            "audit_status": "dashboard_lagging_backend" if lagging else "dashboard_operationally_bound",
        },
        "backend": {
            "route_domain_counts": _route_domain_counts(routes),
            "duplicate_routes": _duplicate_route_report(routes)[:200],
            "routes": routes,
        },
        "frontend": {key: value for key, value in frontend.items() if key != "all_text_lower"},
        "capabilities": capabilities,
        "gaps": {
            "backend_available_dashboard_missing": backend_available_dashboard_missing,
            "button_without_fetch_binding": button_without_fetch,
            "all_lagging_required_capabilities": lagging,
        },
        "next_recommended_build": {
            "id": "S1323-S1350",
            "name": "Dashboard Operations Binding Plan and Active Control Map",
            "purpose": "Create a concrete active-control map from this audit so each required backend capability has a visible dashboard button, fetch binding, result pane, disabled/blocked authority proof, and test coverage.",
        },
        "blocked_authority_preserved": [
            "live_web_execution",
            "search_provider_execution",
            "browser_execution",
            "network_requests",
            "body_reads",
            "autonomous_crawling",
            "automatic_updates",
            "runtime_mutation",
            "runtime_truth_mutation",
            "package_download_install",
            "command_execution",
        ],
    }

    if write_report:
        reports = root / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = reports / f"S1295_S1322_SYSTEM_DASHBOARD_GAP_AUDIT_{stamp}.json"
        md_path = reports / f"S1295_S1322_SYSTEM_DASHBOARD_GAP_AUDIT_{stamp}.md"
        report["report_paths"] = {"json": str(json_path), "markdown": str(md_path)}
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text(_markdown_report(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def _markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Claire System vs Dashboard Operation Gap Audit",
        "",
        f"- Version: `{report['audit_version']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Backend routes: **{summary['backend_route_count']}**",
        f"- Frontend fetches found: **{summary['frontend_fetch_count']}**",
        f"- Frontend buttons found: **{summary['frontend_button_count']}**",
        f"- Required capabilities: **{summary['required_capability_count']}**",
        f"- Bound required capabilities: **{summary['bound_required_capability_count']}**",
        f"- Lagging required capabilities: **{summary['lagging_required_capability_count']}**",
        f"- Dashboard operational binding score: **{summary['dashboard_operational_binding_score']}%**",
        f"- Audit status: **{summary['audit_status']}**",
        "",
        "## Capability gap table",
        "",
        "| Capability | Backend routes | Fetch bound | Button present | Status |",
        "|---|---:|---|---|---|",
    ]
    for cap in report["capabilities"]:
        lines.append(
            f"| {cap['label']} | {cap['backend_route_count']} | {cap['frontend_fetch_bound']} | {cap['button_present']} | `{cap['status']}` |"
        )
    lines.extend(["", "## Lagging required capabilities", ""])
    lagging = report["gaps"]["all_lagging_required_capabilities"]
    if not lagging:
        lines.append("No lagging required capabilities detected.")
    else:
        for cap in lagging:
            lines.append(f"- **{cap['label']}** — `{cap['status']}` — {cap['gap']}")
    lines.extend(["", "## Next recommended build", ""])
    next_build = report["next_recommended_build"]
    lines.append(f"- **{next_build['id']} — {next_build['name']}**")
    lines.append(f"- {next_build['purpose']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build_system_dashboard_gap_audit(Path.cwd(), write_report=True)
    summary = report["summary"]
    print("[Claire System vs Dashboard Operation Gap Audit]")
    print(f"Version: {AUDIT_VERSION}")
    print(f"Backend routes: {summary['backend_route_count']}")
    print(f"Frontend fetches: {summary['frontend_fetch_count']}")
    print(f"Frontend buttons: {summary['frontend_button_count']}")
    print(f"Required capabilities: {summary['required_capability_count']}")
    print(f"Bound required capabilities: {summary['bound_required_capability_count']}")
    print(f"Lagging required capabilities: {summary['lagging_required_capability_count']}")
    print(f"Binding score: {summary['dashboard_operational_binding_score']}%")
    print(f"Audit status: {summary['audit_status']}")
    print(f"JSON report: {report['report_paths']['json']}")
    print(f"Markdown report: {report['report_paths']['markdown']}")
    if report["gaps"]["all_lagging_required_capabilities"]:
        print("\nTop dashboard gaps:")
        for cap in report["gaps"]["all_lagging_required_capabilities"][:20]:
            print(f"- {cap['label']}: {cap['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
