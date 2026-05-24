from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DOCS_RESPONSE_DIR = Path("C:/Users/craig/OneDrive/Desktop/Docs Main/swagger ui json resp")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def response_files(root: Path | str | None = None) -> list[Path]:
    base = Path(root) if root is not None else DOCS_RESPONSE_DIR
    return sorted(base.glob("response_*.json")) if base.exists() else []


def _governance_flags(payload: dict[str, Any]) -> dict[str, Any]:
    governance = payload.get("governance", {}) if isinstance(payload.get("governance"), dict) else {}
    policy = payload.get("policy", {}) if isinstance(payload.get("policy"), dict) else {}
    merged = {**policy, **governance}
    return {
        "review_required": merged.get("review_required"),
        "operator_review_required": merged.get("operator_review_required"),
        "manual_enable_required": payload.get("manual_enable_required") or payload.get("manual_enable") or merged.get("manual_enable_required"),
        "fail_closed": merged.get("fail_closed"),
        "runtime_truth_mutated": merged.get("runtime_truth_mutated"),
        "autonomous_execution": merged.get("autonomous_execution") or merged.get("autonomous_execution_enabled"),
        "automatic_updates": merged.get("automatic_updates") or merged.get("automatic_updates_enabled"),
        "uncontrolled_browsing": merged.get("uncontrolled_browsing") or merged.get("uncontrolled_browsing_enabled"),
    }


def _route_values(payload: dict[str, Any]) -> list[str]:
    routes: list[str] = []
    for key in ("routes", "canonical_paths", "compatibility_paths", "required_routes"):
        value = payload.get(key)
        if isinstance(value, dict):
            routes.extend(str(item) for item in value.values() if str(item).startswith("/"))
        elif isinstance(value, list):
            routes.extend(str(item) for item in value if str(item).startswith("/"))
    return sorted(set(routes))


def classify_response(payload: dict[str, Any]) -> str:
    keys = set(payload)
    if {"result_cards", "visible_result_count"} <= keys:
        return "governed_search_response"
    if {"provider_probe_status", "operator_probe_ready"} & keys or "provider_probe" in str(payload.get("routes", {})):
        return "provider_probe_status"
    if "capabilities" in keys and "backend_search_available" in keys:
        return "operator_search_capabilities"
    if "route_table" in keys or "required_routes" in keys:
        return "route_contract"
    if "continuous_runtime_status" in keys or "selected_route" in keys:
        return "runtime_dashboard_state"
    return "other"


def extract_post_ui_response_reference(root: Path | str | None = None) -> dict[str, Any]:
    files = response_files(root)
    records: list[dict[str, Any]] = []
    route_counter: Counter[str] = Counter()
    class_counter: Counter[str] = Counter()
    contract_versions: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    governance_violations: list[dict[str, Any]] = []

    for path in files:
        payload = read_json(path, {})
        if not isinstance(payload, dict):
            continue
        response_class = classify_response(payload)
        class_counter[response_class] += 1
        if payload.get("contract_version"):
            contract_versions[str(payload.get("contract_version"))] += 1
        if payload.get("status"):
            statuses[str(payload.get("status"))] += 1
        routes = _route_values(payload)
        route_counter.update(routes)
        flags = _governance_flags(payload)
        expected_safe = {
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
            "fail_closed": True,
        }
        for key, expected in expected_safe.items():
            if flags.get(key) is not None and flags.get(key) is not expected:
                governance_violations.append({"file": path.name, "field": key, "value": flags.get(key), "expected": expected})
        records.append(
            {
                "file": path.name,
                "response_class": response_class,
                "contract_version": payload.get("contract_version") or payload.get("version"),
                "status": payload.get("status"),
                "query": payload.get("query"),
                "visible_result_count": payload.get("visible_result_count"),
                "routes": routes,
                "governance": flags,
                "result_card_count": len(payload.get("result_cards", [])) if isinstance(payload.get("result_cards"), list) else 0,
            }
        )

    required_surface_contracts = {
        "governed_search_response": class_counter.get("governed_search_response", 0) >= 1,
        "provider_probe_status": class_counter.get("provider_probe_status", 0) >= 1,
        "operator_search_capabilities": class_counter.get("operator_search_capabilities", 0) >= 1,
        "manual_enable_or_review_required": any(
            item.get("governance", {}).get("manual_enable_required") or item.get("governance", {}).get("review_required")
            for item in records
        ),
        "fail_closed_no_truth_mutation": not governance_violations,
        "canonical_search_routes_recovered": any(route.startswith("/api/dashboard/search") or route.startswith("/api/search/") for route in route_counter),
    }
    return {
        "schema_version": "claire.post_ui_response_reference.v1",
        "generated_at": utc_now(),
        "status": "ready" if all(required_surface_contracts.values()) else "needs_review",
        "source": str(Path(root) if root is not None else DOCS_RESPONSE_DIR),
        "documents_used_as_runtime_programming": False,
        "file_count": len(files),
        "record_count": len(records),
        "response_classes": dict(sorted(class_counter.items())),
        "contract_versions": dict(sorted(contract_versions.items())),
        "statuses": dict(sorted(statuses.items())),
        "recovered_routes": [
            {"route": route, "seen_count": count}
            for route, count in route_counter.most_common()
        ],
        "required_surface_contracts": required_surface_contracts,
        "governance_violations": governance_violations,
        "records": records,
        "home_surface_requirements": [
            "Search must be visible as a command-center surface, not hidden as a backend-only endpoint.",
            "Provider probe must fail closed until manually enabled or explicitly configured.",
            "Search results must render visible result cards while remaining metadata-only until promotion.",
            "Compatibility paths may exist as operator convenience, but canonical paths must remain clear.",
            "No search/probe response may mutate runtime truth or perform autonomous update actions.",
        ],
    }


def persist_post_ui_response_reference(
    root: Path | str | None = None,
    output: Path | str | None = None,
) -> dict[str, Any]:
    payload = extract_post_ui_response_reference(root)
    out = Path(output) if output is not None else Path.cwd() / "reports" / "POST_UI_RESPONSE_REFERENCE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    md.write_text(render_markdown(payload), encoding="utf-8")
    payload["paths"] = {"json": str(out), "markdown": str(md)}
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Claire Post-UI Response Reference",
        "",
        f"Status: `{payload.get('status')}`",
        f"Files: `{payload.get('file_count')}`",
        f"Records: `{payload.get('record_count')}`",
        "",
        "## Surface Contracts",
        "",
    ]
    contracts = payload.get("required_surface_contracts", {}) if isinstance(payload.get("required_surface_contracts"), dict) else {}
    lines.extend(f"- {key}: `{value}`" for key, value in contracts.items())
    lines.extend(["", "## Requirements", ""])
    lines.extend(f"- {item}" for item in payload.get("home_surface_requirements", []))
    return "\n".join(lines) + "\n"
