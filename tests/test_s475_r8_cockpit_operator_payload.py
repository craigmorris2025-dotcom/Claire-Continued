from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "s475_r8_cockpit_operator_payload_report.json"


DASHBOARD_CANDIDATES = [
    ROOT / "frontend" / "cockpit" / "index.html",
    ROOT / "frontend" / "cockpit" / "shell" / "cockpit_shell.html",
    ROOT / "frontend" / "command_center" / "modern" / "index.html",
]


def _load_report() -> dict:
    assert REPORT_PATH.exists(), f"Missing S475-R8 cockpit operator payload report: {REPORT_PATH}"
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_s475_r8_cockpit_operator_payload_report_exists_and_is_current():
    report = _load_report()
    assert report["status"] in {"ok", "browser_launch_disabled_in_tests"}
    assert report["stage"] in {"S475-R8", "S475-R8-browser-test-repair"}
    assert report["cockpit_operator_payload"]["backend_owned_truth"] is True
    assert report["cockpit_operator_payload"]["dashboard_presentation_only"] is True


def test_s475_r8_plateau_report_points_to_dashboard_browser():
    """The plateau report must describe the dashboard browser target without opening it.

    This test intentionally does not call webbrowser.open(), os.startfile(), subprocess.Popen(),
    or any platform browser launch path. Pytest must validate the payload contract only.
    """
    report = _load_report()
    browser = report["dashboard_browser"]

    assert browser["url"].startswith("http://127.0.0.1:")
    assert browser["route"] in {"/", "/dashboard", "/cockpit"}
    assert browser["launch_policy"] == "manual_operator_only"
    assert browser["pytest_browser_launch_performed"] is False
    assert browser["os_browser_launch_allowed_in_tests"] is False


def test_s475_r8_dashboard_file_candidate_exists():
    existing = [path for path in DASHBOARD_CANDIDATES if path.exists()]
    assert existing, "No known cockpit/dashboard HTML entry point exists."


def test_s475_r8_preserves_web_and_runtime_blocks():
    report = _load_report()
    blocks = report["preserved_blocks"]
    assert blocks["live_web_execution_enabled"] is False
    assert blocks["browser_execution_enabled"] is False
    assert blocks["network_request_performed"] is False
    assert blocks["body_read_allowed"] is False
    assert blocks["autonomous_crawling_enabled"] is False
    assert blocks["automatic_updates_enabled"] is False
    assert blocks["runtime_mutation_enabled"] is False
    assert blocks["package_download_performed"] is False
    assert blocks["package_install_performed"] is False
    assert blocks["command_execution_enabled"] is False
