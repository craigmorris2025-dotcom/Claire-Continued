
from __future__ import annotations

import importlib
import json
from pathlib import Path


def make_artifacts(root: Path) -> None:
    artifacts = {
        "output/unified_operator_payload/unified_backend_operator_payload.json": "unified_backend_operator_payload",
        "output/operator_runtime_snapshots/operator_state_snapshot.json": "operator_state_snapshot",
        "output/operator_runtime_snapshots/bounded_runtime_summary.json": "bounded_runtime_summary",
        "output/operator_state_digest/operator_current_state_digest.json": "operator_current_state_digest",
        "output/operator_state_digest/operator_alert_summary.json": "operator_alert_summary",
        "output/operator_state_digest/s41_operator_runtime_snapshot_readiness_report.json": "s41_operator_runtime_snapshot_readiness_report",
        "output/operator_route_plateau/s41_operator_route_plateau_report.json": "s41_operator_route_plateau_report",
    }
    for item, record_type in artifacts.items():
        path = root / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "record_type": record_type,
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
            "status": "ready",
        }), encoding="utf-8")


def test_s42r21_builds_isolated_test_app(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_route_harness")
    app = module.build_isolated_operator_route_test_app(tmp_path)
    paths = {route.path for route in app.routes}

    assert "/operator/payload" in paths
    assert "/operator/routes" in paths


def test_s42r22_to_r24_probes_routes_read_only(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_route_harness")
    make_artifacts(tmp_path)
    report = module.probe_operator_routes_isolated(tmp_path)

    assert report["probe_count"] == 7
    assert report["ok_count"] == 7
    assert report["available_count"] == 7
    assert report["app_py_patch_required"] is False
    assert report["live_server_required"] is False
    assert report["runtime_truth_mutation_allowed"] is False
    for result in report["results"]:
        assert result["status_code"] == 200
        assert result["mutating"] is False
        assert result["response_mode"] == "read_only_artifact"
        assert result["runtime_truth_mutation_allowed"] is False


def test_s42r25_to_r27_verification_and_plateau(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_route_harness")
    make_artifacts(tmp_path)
    report = module.probe_operator_routes_isolated(tmp_path)
    verification = module.verify_isolated_operator_route_probe(report)
    plateau = module.build_s42_route_harness_plateau(report, verification)

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["app_py_patch_required"] is False
    assert plateau["status"] == "s42_route_harness_ready"
    assert plateau["next_phase"] == "S43 controlled app integration discovery and mounted-route availability verification"


def test_s42r28_writes_harness_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.operator_route_harness")
    make_artifacts(tmp_path)
    result = module.write_s42_live_route_harness(tmp_path, tmp_path / "out")

    assert set(result) == {"probe_report", "verification", "plateau"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
