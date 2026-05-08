from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from claire.runtime.dashboard_e2e_first_use import (  # noqa: E402
    dashboard_e2e_capability_manifest,
    read_latest_dashboard_e2e_result,
    run_dashboard_e2e_first_use,
)


def test_v17_51_manifest_exists_and_registers_dashboard_buttons():
    path = ROOT / "manifests" / "v17_51_dashboard_e2e_first_use_manifest.json"
    assert path.exists()
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["version"] == "17.51"
    assert "Run First-Use E2E Check" in manifest["dashboard_buttons"]
    assert "POST /dashboard/e2e/first-use/run" in manifest["dashboard_routes_to_register"]
    assert manifest["governance_preserved"]["bounded_orchestration"] is True
    assert manifest["governance_preserved"]["runtime_isolation"] is True


def test_v17_51_runtime_manifest_is_executable():
    manifest = dashboard_e2e_capability_manifest()
    assert manifest["version"] == "17.51"
    button_ids = {button["id"] for button in manifest["dashboard_buttons"]}
    assert "run-dashboard-first-use-e2e" in button_ids
    assert "view-dashboard-first-use-e2e-latest" in button_ids
    assert manifest["governance"]["network_free_local_smoke_test"] is True


def test_v17_51_dashboard_action_creates_auditable_result_file():
    result = run_dashboard_e2e_first_use({"source": "pytest", "action": "first_use"})
    payload = result.to_dict()
    assert payload["version"] == "17.51"
    assert payload["status"] in {"passed", "passed_with_launch_warnings", "failed"}
    assert payload["governance"]["runtime_isolation_preserved"] is True
    assert payload["governance"]["bounded_orchestration_preserved"] is True
    assert payload["governance"]["external_network_required"] is False
    output_path = ROOT / payload["output_path"]
    assert output_path.exists()
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["run_id"] == payload["run_id"]
    latest = read_latest_dashboard_e2e_result()
    assert latest["run_id"] == payload["run_id"]
    check_names = {check["name"] for check in latest["checks"]}
    assert "manifest_integrity_check" in check_names
    assert "dashboard_capability_check" in check_names


def test_v17_51_api_route_module_imports_without_side_effects():
    import claire.api.routes_dashboard_e2e as routes

    assert hasattr(routes, "router")
