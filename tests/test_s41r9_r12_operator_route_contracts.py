
from __future__ import annotations

import importlib
import json
from pathlib import Path


def make_artifacts(root: Path) -> None:
    paths = [
        "output/unified_operator_payload/unified_backend_operator_payload.json",
        "output/operator_runtime_snapshots/operator_state_snapshot.json",
        "output/operator_runtime_snapshots/bounded_runtime_summary.json",
        "output/operator_state_digest/operator_current_state_digest.json",
        "output/operator_state_digest/operator_alert_summary.json",
        "output/operator_state_digest/s41_operator_runtime_snapshot_readiness_report.json",
    ]
    for item in paths:
        path = root / item
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "record_type": path.stem,
            "status": "ready",
            "runtime_truth_mutation_allowed": False,
        }), encoding="utf-8")


def test_s41r9_route_registry_is_read_only(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_route_contracts")
    make_artifacts(tmp_path)
    registry = module.build_operator_route_contract_registry(tmp_path)

    assert registry["backend_owns_truth"] is True
    assert registry["cockpit_presentation_only"] is True
    assert registry["route_count"] == 6
    assert registry["available_route_artifact_count"] == 6
    assert registry["runtime_truth_mutation_allowed"] is False
    for contract in registry["contracts"]:
        assert contract["method"] == "GET"
        assert contract["mutating"] is False
        assert contract["runtime_truth_mutation_allowed"] is False


def test_s41r10_response_index_maps_artifacts(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_route_contracts")
    make_artifacts(tmp_path)
    registry = module.build_operator_route_contract_registry(tmp_path)
    index = module.build_operator_route_response_index(tmp_path, registry)

    assert index["route_response_count"] == 6
    assert index["source_route_registry_sha256"] == registry["route_registry_sha256"]
    assert index["runtime_truth_mutation_allowed"] is False
    for response in index["responses"]:
        assert response["artifact_available"] is True
        assert response["mutating"] is False


def test_s41r11_route_contract_verification_passes(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_route_contracts")
    make_artifacts(tmp_path)
    registry = module.build_operator_route_contract_registry(tmp_path)
    index = module.build_operator_route_response_index(tmp_path, registry)
    report = module.verify_operator_route_contracts(registry, index)

    assert report["verification_ok"] is True
    assert report["failures"] == []
    assert report["runtime_truth_mutation_allowed"] is False


def test_s41r12_writes_operator_route_contract_files(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_operator_route_contracts")
    make_artifacts(tmp_path)
    result = module.write_operator_route_contracts(tmp_path, tmp_path / "out")

    assert set(result) == {"registry", "response_index", "verification"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
