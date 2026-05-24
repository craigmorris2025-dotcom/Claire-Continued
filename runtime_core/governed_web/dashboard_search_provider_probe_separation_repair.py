from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

CONTRACT_VERSION = "v18.73.2.dashboard_search_provider_probe_separation_repair"

DASHBOARD_PATHS = [
    Path("frontend/command_center/modern/index.html"),
    Path("src/frontend/command_center/modern/index.html"),
]
PRIMARY_JS_NAME = "dashboard_primary_web_search_binding.js"
PRIMARY_START = "<!-- CLAIRE_PRIMARY_WEB_SEARCH_PANEL_START -->"
PRIMARY_END = "<!-- CLAIRE_PRIMARY_WEB_SEARCH_PANEL_END -->"
PRIMARY_SCRIPT_MARKER = "<!-- CLAIRE_PRIMARY_WEB_SEARCH_SCRIPT -->"

REQUIRED_PRIMARY_IDS = [
    "claire-primary-web-search-panel",
    "claire-primary-web-search-form",
    "claire-primary-web-search-query",
    "claire-primary-web-search-button",
    "claire-primary-web-search-status",
    "claire-primary-web-search-results",
]

REQUIRED_JS_TEXT = [
    "window.ClairePrimaryWebSearch",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
    "runPrimaryWebSearch",
    "claire-primary-web-search-results",
]

PROVIDER_CLARITY_TEXT = [
    "Advanced / Manual Provider Probe",
    "Normal searches should use Governed Live Web Search above.",
    "This panel is only for explicit operator provider tests.",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class DashboardSearchSeparationPolicy:
    primary_search_is_normal_web_search: bool = True
    provider_probe_is_advanced_manual_test: bool = True
    provider_probe_explicit_enable_required: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_search_is_normal_web_search": self.primary_search_is_normal_web_search,
            "provider_probe_is_advanced_manual_test": self.provider_probe_is_advanced_manual_test,
            "provider_probe_explicit_enable_required": self.provider_probe_explicit_enable_required,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
        }


def inspect_dashboard_search_provider_probe_separation(root: Path = Path(".")) -> Dict[str, Any]:
    policy = DashboardSearchSeparationPolicy()
    rows: List[Dict[str, Any]] = []

    for rel in DASHBOARD_PATHS:
        dashboard = root / rel
        html = dashboard.read_text(encoding="utf-8", errors="ignore") if dashboard.exists() else ""
        js = dashboard.parent / PRIMARY_JS_NAME
        js_text = js.read_text(encoding="utf-8", errors="ignore") if js.exists() else ""

        rows.append({
            "dashboard_path": str(rel),
            "dashboard_exists": dashboard.exists(),
            "primary_panel_present": PRIMARY_START in html and PRIMARY_END in html,
            "primary_script_present": PRIMARY_SCRIPT_MARKER in html and PRIMARY_JS_NAME in html,
            "missing_primary_ids": [item for item in REQUIRED_PRIMARY_IDS if item not in html],
            "provider_clarity_missing": [item for item in PROVIDER_CLARITY_TEXT if item not in html],
            "primary_js_path": str(js),
            "primary_js_exists": js.exists(),
            "primary_js_missing_text": [item for item in REQUIRED_JS_TEXT if item not in js_text],
        })

    ready_rows = [
        row for row in rows
        if row["dashboard_exists"]
        and row["primary_panel_present"]
        and row["primary_script_present"]
        and row["missing_primary_ids"] == []
        and row["provider_clarity_missing"] == []
        and row["primary_js_exists"]
        and row["primary_js_missing_text"] == []
    ]

    ready = bool(ready_rows)

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "dashboard_search_separation_ready" if ready else "dashboard_search_separation_incomplete",
        "created_at": _now(),
        "ready": ready,
        "rows": rows,
        "operator_instruction": "Use Governed Live Web Search for normal web search. Use Advanced / Manual Provider Probe only for explicit operator provider tests.",
        "policy": policy.to_dict(),
        "governance": {
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
            "operator_review_required": True,
        },
    }


def build_dashboard_search_separation_report(root: Path = Path(".")) -> Dict[str, Any]:
    inspection = inspect_dashboard_search_provider_probe_separation(root)
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "ready" if inspection["ready"] else "incomplete",
        "created_at": _now(),
        "inspection": inspection,
        "normal_web_search_endpoint": "/api/dashboard/search/live",
        "google_smoke_endpoint": "/api/dashboard/search/smoke/google",
        "provider_probe_endpoint": "/api/dashboard/search/provider/probe",
        "expected_normal_search_result": {
            "query": "google",
            "title": "Google",
            "url": "https://www.google.com",
        },
        "policy": DashboardSearchSeparationPolicy().to_dict(),
    }


__all__ = [
    "CONTRACT_VERSION",
    "DashboardSearchSeparationPolicy",
    "build_dashboard_search_separation_report",
    "inspect_dashboard_search_provider_probe_separation",
]
