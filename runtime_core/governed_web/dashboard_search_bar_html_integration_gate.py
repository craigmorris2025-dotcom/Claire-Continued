
# Claire Syntalion v18.60
# Dashboard Search Bar HTML Integration Gate
#
# This module safely inserts a governed live-search UI scaffold into the
# dashboard HTML. It does not execute searches, mutate runtime truth, trigger
# automatic updates, or enable autonomous execution.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CONTRACT_VERSION = "v18.60.dashboard_search_bar_html_integration_gate"

DEFAULT_DASHBOARD_PATH = Path("frontend/command_center/modern/index.html")
DEFAULT_SCRIPT_PATH = "governed_live_search_ui_binding.js"

START_MARKER = "<!-- CLAIRE_GOVERNED_LIVE_SEARCH_START -->"
END_MARKER = "<!-- CLAIRE_GOVERNED_LIVE_SEARCH_END -->"
SCRIPT_MARKER = "<!-- CLAIRE_GOVERNED_LIVE_SEARCH_SCRIPT -->"

REQUIRED_IDS = [
    "claire-governed-live-search-form",
    "claire-governed-live-search-input",
    "claire-governed-live-search-manual-enable",
    "claire-governed-live-search-status",
    "claire-governed-live-search-results",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class DashboardSearchBarHTMLIntegrationPolicy:
    manual_enable_required: bool = True
    review_required: bool = True
    fail_closed: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    backup_before_modify: bool = True
    bounded_html_mutation: bool = True
    frontend_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manual_enable_required": self.manual_enable_required,
            "review_required": self.review_required,
            "fail_closed": self.fail_closed,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "backup_before_modify": self.backup_before_modify,
            "bounded_html_mutation": self.bounded_html_mutation,
            "frontend_only": self.frontend_only,
        }


def build_governed_live_search_html_block() -> str:
    return (
        START_MARKER
        + "\n"
        + '<section class="claire-governed-live-search-panel" data-claire-governed-live-search="true">\n'
        + '  <div class="claire-governed-live-search-header">\n'
        + "    <h2>Governed Live Web Search</h2>\n"
        + "    <p>Review-gated live search. Manual enable is required before results render.</p>\n"
        + "  </div>\n"
        + '  <form id="claire-governed-live-search-form" class="claire-governed-live-search-form">\n'
        + '    <label for="claire-governed-live-search-input">Search the web</label>\n'
        + '    <div class="claire-governed-live-search-row">\n'
        + '      <input id="claire-governed-live-search-input" name="query" type="search" placeholder="Type google and press Search" autocomplete="off" />\n'
        + '      <button type="submit">Search</button>\n'
        + "    </div>\n"
        + '    <label class="claire-governed-live-search-enable">\n'
        + '      <input id="claire-governed-live-search-manual-enable" type="checkbox" />\n'
        + "      Manual governed live-search enable\n"
        + "    </label>\n"
        + '    <div id="claire-governed-live-search-status" class="claire-governed-live-search-status" role="status">Governed live search UI waiting.</div>\n'
        + "  </form>\n"
        + '  <div id="claire-governed-live-search-results" class="claire-governed-live-search-results" aria-live="polite"></div>\n'
        + "</section>\n"
        + END_MARKER
    )


def build_governed_live_search_script_tag(script_path: str = DEFAULT_SCRIPT_PATH) -> str:
    clean_script_path = script_path.strip() or DEFAULT_SCRIPT_PATH
    return SCRIPT_MARKER + "\n" + '<script src="' + clean_script_path + '" defer></script>'


def _default_dashboard_html() -> str:
    return (
        "<!doctype html>\n"
        + '<html lang="en">\n'
        + "<head>\n"
        + '  <meta charset="utf-8" />\n'
        + "  <title>Claire Syntalion Command Center</title>\n"
        + "</head>\n"
        + "<body>\n"
        + "  <main id=\"claire-command-center\">\n"
        + "    <h1>Claire Syntalion</h1>\n"
        + "  </main>\n"
        + "</body>\n"
        + "</html>\n"
    )


def _replace_between_markers(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    if start_marker in text and end_marker in text:
        before = text.split(start_marker, 1)[0]
        after = text.split(end_marker, 1)[1]
        return before.rstrip() + "\n" + replacement + "\n" + after.lstrip()
    return text


def _insert_before_body_end(text: str, block: str) -> str:
    lower = text.lower()
    marker = "</body>"
    index = lower.rfind(marker)
    if index >= 0:
        return text[:index].rstrip() + "\n" + block + "\n" + text[index:]
    return text.rstrip() + "\n" + block + "\n"


def _ensure_script_tag(text: str, script_tag: str) -> str:
    if SCRIPT_MARKER in text:
        before = text.split(SCRIPT_MARKER, 1)[0].rstrip()
        after = text.split(SCRIPT_MARKER, 1)[1]
        after_lines = after.splitlines()
        if after_lines:
            after = "\n".join(after_lines[1:]).lstrip()
        return before + "\n" + script_tag + "\n" + after
    if DEFAULT_SCRIPT_PATH in text:
        return text
    return _insert_before_body_end(text, script_tag)


def integrate_governed_live_search_into_html_text(
    html_text: str,
    *,
    script_path: str = DEFAULT_SCRIPT_PATH,
) -> Dict[str, Any]:
    original = html_text if html_text else _default_dashboard_html()
    block = build_governed_live_search_html_block()
    script_tag = build_governed_live_search_script_tag(script_path)

    if START_MARKER in original and END_MARKER in original:
        updated = _replace_between_markers(original, START_MARKER, END_MARKER, block)
    else:
        updated = _insert_before_body_end(original, block)

    updated = _ensure_script_tag(updated, script_tag)

    missing_ids = [item for item in REQUIRED_IDS if item not in updated]
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "html_integration_ready" if not missing_ids else "html_integration_incomplete",
        "created_at": _utc_now(),
        "html": updated,
        "markers_present": START_MARKER in updated and END_MARKER in updated and SCRIPT_MARKER in updated,
        "required_ids_present": not missing_ids,
        "missing_ids": missing_ids,
        "script_path": script_path,
        "policy": DashboardSearchBarHTMLIntegrationPolicy().to_dict(),
        "governance": {
            "review_required": True,
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "fail_closed": True,
            "frontend_html_only": True,
        },
    }


def apply_governed_live_search_html_integration(
    dashboard_path: Path | str = DEFAULT_DASHBOARD_PATH,
    *,
    script_path: str = DEFAULT_SCRIPT_PATH,
    create_if_missing: bool = True,
    backup: bool = True,
) -> Dict[str, Any]:
    path = Path(dashboard_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existed_before = path.exists()
    if existed_before:
        original = path.read_text(encoding="utf-8")
    elif create_if_missing:
        original = _default_dashboard_html()
    else:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "blocked",
            "reason": "dashboard_html_missing",
            "dashboard_path": str(path),
            "created_at": _utc_now(),
            "policy": DashboardSearchBarHTMLIntegrationPolicy().to_dict(),
            "governance": {
                "review_required": True,
                "runtime_truth_mutated": False,
                "autonomous_execution": False,
                "automatic_updates": False,
                "fail_closed": True,
            },
        }

    backup_path = None
    if backup and existed_before:
        backup_path = path.with_suffix(path.suffix + ".v18_60_backup")
        if not backup_path.exists():
            backup_path.write_text(original, encoding="utf-8")

    result = integrate_governed_live_search_into_html_text(original, script_path=script_path)
    path.write_text(result["html"], encoding="utf-8")

    return {
        "contract_version": CONTRACT_VERSION,
        "status": result["status"],
        "reason": "" if result["status"] == "html_integration_ready" else "missing_required_ids",
        "created_at": _utc_now(),
        "dashboard_path": str(path),
        "existed_before": existed_before,
        "backup_path": str(backup_path) if backup_path else "",
        "markers_present": result["markers_present"],
        "required_ids_present": result["required_ids_present"],
        "missing_ids": result["missing_ids"],
        "script_path": script_path,
        "policy": result["policy"],
        "governance": result["governance"],
    }


__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_DASHBOARD_PATH",
    "DEFAULT_SCRIPT_PATH",
    "DashboardSearchBarHTMLIntegrationPolicy",
    "END_MARKER",
    "REQUIRED_IDS",
    "SCRIPT_MARKER",
    "START_MARKER",
    "apply_governed_live_search_html_integration",
    "build_governed_live_search_html_block",
    "build_governed_live_search_script_tag",
    "integrate_governed_live_search_into_html_text",
]
