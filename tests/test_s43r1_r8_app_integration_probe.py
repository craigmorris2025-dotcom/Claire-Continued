
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
        "output/operator_state_digest/s41_operator_runtime_snapshot_readiness_report.json": "s41_readiness",
        "output/operator_route_plateau/s41_operator_route_plateau_report.json": "s41_routes",
    }
    for item, record_type in artifacts.items():
        path = root / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "record_type": record_type,
            "status": "ready",
            "runtime_truth_mutation_allowed": False,
            "automatic_update_allowed": False,
        }), encoding="utf-8")


def test_s43r1_discovers_primary_app_non_invasively():
    module = importlib.import_module("claire.api.s43_app_integration_probe")
    discovery = module.discover_primary_app()

    assert discovery["app_py_patch_required"] is False
    assert discovery["non_invasive"] is True
    assert discovery["runtime_truth_mutation_allowed"] is False
    assert discovery["automatic_update_allowed"] is False
    assert len(discovery["discovery_sha256"]) == 64


def test_s43r2_to_r5_probe_mounted_routes(tmp_path: Path):
    module = importlib.import_module("claire.api.s43_app_integration_probe")
    make_artifacts(tmp_path)
    probe = module.probe_mounted_operator_routes(tmp_path)

    assert probe["probe_count"] == 7
    assert probe["ok_count"] == 7
    assert probe["available_count"] == 7
    assert probe["app_py_patch_required"] is False
    assert probe["runtime_truth_mutation_allowed"] is False
    for item in probe["results"]:
        assert item["status_code"] == 200
        assert item["mutating"] is False
        assert item["response_mode"] == "read_only_artifact"


def test_s43r6_to_r7_verification_passes(tmp_path: Path):
    module = importlib.import_module("claire.api.s43_app_integration_probe")
    make_artifacts(tmp_path)
    discovery = module.discover_primary_app()
    probe = module.probe_mounted_operator_routes(tmp_path)
    verification = module.verify_mounted_operator_routes(discovery, probe)

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["app_py_patch_required"] is False
    assert verification["runtime_truth_mutation_allowed"] is False


def test_s43r8_writes_integration_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.s43_app_integration_probe")
    make_artifacts(tmp_path)
    result = module.write_s43_app_integration_probe(tmp_path, tmp_path / "out")

    assert set(result) == {"discovery", "probe", "verification", "report"}
    for value in result.values():
        assert Path(value).exists()

    report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
    assert report["status"] == "s43_app_integration_probe_ready"
    assert report["next_phase"] == "S43R9-R16 app route exposure adapter and swagger-visible route registration plan"
