
from __future__ import annotations

import importlib
import json
from pathlib import Path


def sample_registry():
    return {
        "route_registry_sha256": "r" * 64,
        "contracts": [
            {
                "route": "/operator/payload",
                "method": "GET",
                "artifact": "output/unified_operator_payload/unified_backend_operator_payload.json",
                "available": True,
                "response_mode": "read_only_artifact",
                "mutating": False,
                "route_contract_sha256": "a" * 64,
                "runtime_truth_mutation_allowed": False,
                "automatic_update_allowed": False,
            },
            {
                "route": "/operator/alerts",
                "method": "GET",
                "artifact": "output/operator_state_digest/operator_alert_summary.json",
                "available": False,
                "response_mode": "read_only_artifact",
                "mutating": False,
                "route_contract_sha256": "b" * 64,
                "runtime_truth_mutation_allowed": False,
                "automatic_update_allowed": False,
            },
        ],
    }


def sample_response_index():
    return {
        "route_response_index_sha256": "i" * 64,
        "responses": [
            {
                "route": "/operator/payload",
                "artifact_available": True,
                "route_response_sha256": "c" * 64,
            },
            {
                "route": "/operator/alerts",
                "artifact_available": False,
                "route_response_sha256": "d" * 64,
            },
        ],
    }


def test_s41r13_builds_route_plateau_index():
    module = importlib.import_module("runtime_core.api.governed_operator_route_plateau")
    index = module.build_operator_route_plateau_index(sample_registry(), sample_response_index())

    assert index["route_count"] == 2
    assert index["available_route_artifact_count"] == 1
    assert index["runtime_truth_mutation_allowed"] is False
    assert index["automatic_update_allowed"] is False
    assert index["route_wiring_installed"] is False
    assert len(index["route_plateau_index_sha256"]) == 64


def test_s41r14_missing_artifact_registry():
    module = importlib.import_module("runtime_core.api.governed_operator_route_plateau")
    index = module.build_operator_route_plateau_index(sample_registry(), sample_response_index())
    missing = module.build_missing_route_artifact_registry(index)

    assert missing["missing_count"] == 1
    assert missing["missing_artifacts"][0]["route"] == "/operator/alerts"
    assert missing["runtime_truth_mutation_allowed"] is False
    assert missing["route_wiring_installed"] is False


def test_s41r15_plateau_verification_passes_read_only_contracts():
    module = importlib.import_module("runtime_core.api.governed_operator_route_plateau")
    index = module.build_operator_route_plateau_index(sample_registry(), sample_response_index())
    missing = module.build_missing_route_artifact_registry(index)
    verification = module.verify_operator_route_plateau(index, missing)

    assert verification["verification_ok"] is True
    assert verification["failures"] == []
    assert verification["runtime_truth_mutation_allowed"] is False
    assert verification["route_wiring_installed"] is False


def test_s41r16_writes_route_plateau_artifacts(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_operator_route_plateau")
    source = tmp_path / "output" / "operator_route_contracts"
    source.mkdir(parents=True)
    (source / "operator_route_contract_registry.json").write_text(json.dumps(sample_registry()), encoding="utf-8")
    (source / "operator_route_response_index.json").write_text(json.dumps(sample_response_index()), encoding="utf-8")

    result = module.write_s41_operator_route_plateau(tmp_path, tmp_path / "out")
    assert set(result) == {"plateau_index", "missing_registry", "verification", "report"}
    for value in result.values():
        assert Path(value).exists()

    report = json.loads(Path(result["report"]).read_text(encoding="utf-8"))
    assert report["status"] == "s41_route_plateau_ready"
    assert report["route_wiring_installed"] is False
    assert report["next_phase"] == "S42 read-only route exposure through existing router boundary"
