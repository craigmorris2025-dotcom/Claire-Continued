from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

CONTRACT_VERSION = "v18.73.root_consolidation_single_dashboard_launcher"

ROOT = Path(".")
DASHBOARD_PATHS = [
    Path("frontend/command_center/modern/index.html"),
    Path("src/frontend/command_center/modern/index.html"),
]
BRIDGE_NAME = "dashboard_file_origin_fetch_bridge.js"
SCRIPT_MARKER = "<!-- CLAIRE_DASHBOARD_FILE_ORIGIN_FETCH_BRIDGE -->"

ARCHIVE_DIRS = [
    Path("tools/root_archive/v18_73_review_batches"),
    Path("tools/installers/v18"),
    Path("audits/v18_73_root_consolidation"),
]

REQUIRED_LAUNCHER_TEXT = [
    "CLAIRE_ALLOW_CONTROLLED_HEAD_PROBE=1",
    "CLAIRE_ALLOW_CONTROLLED_METADATA_GET=1",
    "CLAIRE_ALLOW_CONTROLLED_LIMITED_BODY_GET=1",
    "CLAIRE_ALLOW_REAL_SEARCH_PROVIDER=1",
    "frontend\\command_center\\modern\\index.html",
    "python main.py",
]

REQUIRED_BRIDGE_TEXT = [
    "window.ClaireDashboardWebActivationBridge",
    "http://localhost:8000",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
    "window.fetch = bridgeFetch",
    "runLiveSearch",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class RootConsolidationPolicy:
    delete_files: bool = False
    archive_only: bool = True
    single_root_dashboard_launcher: bool = True
    immutable_runtime_truth: bool = True
    runtime_truth_mutated: bool = False
    autonomous_execution_enabled: bool = False
    automatic_updates_enabled: bool = False
    uncontrolled_browsing_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "delete_files": self.delete_files,
            "archive_only": self.archive_only,
            "single_root_dashboard_launcher": self.single_root_dashboard_launcher,
            "immutable_runtime_truth": self.immutable_runtime_truth,
            "runtime_truth_mutated": self.runtime_truth_mutated,
            "autonomous_execution_enabled": self.autonomous_execution_enabled,
            "automatic_updates_enabled": self.automatic_updates_enabled,
            "uncontrolled_browsing_enabled": self.uncontrolled_browsing_enabled,
        }


def inspect_single_dashboard_launcher_state(root: Path = ROOT) -> Dict[str, Any]:
    policy = RootConsolidationPolicy()
    launcher = root / "LAUNCH_CLAIRE.bat"
    launcher_text = launcher.read_text(encoding="utf-8", errors="ignore") if launcher.exists() else ""
    root_bats = sorted(path.name for path in root.glob("*.bat"))

    dashboard_rows: List[Dict[str, Any]] = []
    bridge_rows: List[Dict[str, Any]] = []

    for dashboard in DASHBOARD_PATHS:
        path = root / dashboard
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        dashboard_rows.append({
            "path": str(dashboard),
            "exists": path.exists(),
            "bridge_script_present": SCRIPT_MARKER in text and BRIDGE_NAME in text,
        })

        bridge = path.parent / BRIDGE_NAME
        bridge_text = bridge.read_text(encoding="utf-8", errors="ignore") if bridge.exists() else ""
        bridge_rows.append({
            "path": str(bridge.relative_to(root)) if bridge.exists() else str(dashboard.parent / BRIDGE_NAME),
            "exists": bridge.exists(),
            "missing_required_text": [item for item in REQUIRED_BRIDGE_TEXT if item not in bridge_text],
        })

    launcher_missing = [item for item in REQUIRED_LAUNCHER_TEXT if item not in launcher_text]
    ready_dashboards = [row for row in dashboard_rows if row["exists"] and row["bridge_script_present"]]
    ready_bridges = [row for row in bridge_rows if row["exists"] and not row["missing_required_text"]]

    ready = (
        launcher.exists()
        and launcher_missing == []
        and root_bats == ["LAUNCH_CLAIRE.bat"]
        and bool(ready_dashboards)
        and bool(ready_bridges)
    )

    return {
        "contract_version": CONTRACT_VERSION,
        "status": "single_dashboard_launcher_ready" if ready else "single_dashboard_launcher_incomplete",
        "created_at": _now(),
        "ready": ready,
        "root_bat_files": root_bats,
        "launcher_exists": launcher.exists(),
        "launcher_missing_required_text": launcher_missing,
        "dashboard_rows": dashboard_rows,
        "bridge_rows": bridge_rows,
        "archive_dirs": [str(path) for path in ARCHIVE_DIRS],
        "policy": policy.to_dict(),
        "governance": {
            "runtime_truth_mutated": False,
            "autonomous_execution": False,
            "automatic_updates": False,
            "uncontrolled_browsing": False,
            "archive_only": True,
        },
    }


def build_root_consolidation_report(root: Path = ROOT) -> Dict[str, Any]:
    state = inspect_single_dashboard_launcher_state(root)
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "root_consolidation_ready" if state["ready"] else "root_consolidation_incomplete",
        "created_at": _now(),
        "state": state,
        "operator_next_step": (
            "Run LAUNCH_CLAIRE.bat, wait for backend startup, use the dashboard search bar with google."
            if state["ready"] else
            "Review state.root_bat_files and bridge_rows before manual dashboard test."
        ),
        "expected_dashboard_result": {
            "query": "google",
            "title": "Google",
            "url": "https://www.google.com",
        },
        "policy": RootConsolidationPolicy().to_dict(),
    }


__all__ = [
    "CONTRACT_VERSION",
    "RootConsolidationPolicy",
    "build_root_consolidation_report",
    "inspect_single_dashboard_launcher_state",
]
