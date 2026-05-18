
from __future__ import annotations

import importlib
import json
from pathlib import Path


def make_plateau(root: Path) -> None:
    plateau = root / "output" / "manual_promotion_plateau"
    plateau.mkdir(parents=True)
    (plateau / "s39_manual_promotion_plateau_report.json").write_text(json.dumps({
        "status": "plateau_ready",
        "runtime_truth_mutation_allowed": False,
        "promotion_effect": "none",
    }), encoding="utf-8")
    (plateau / "manual_promotion_package_index.json").write_text(json.dumps({
        "candidate_count": 1,
        "runtime_truth_mutation_allowed": False,
        "promotion_effect": "none",
    }), encoding="utf-8")
    (plateau / "blocked_promotion_candidate_registry.json").write_text(json.dumps({
        "blocked_count": 0,
        "runtime_truth_mutation_allowed": False,
    }), encoding="utf-8")
    (plateau / "promotion_package_replay_verification.json").write_text(json.dumps({
        "replay_ok": True,
        "runtime_truth_mutation_allowed": False,
    }), encoding="utf-8")


def test_s40r1_registry_locks_truth_ownership(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_backend_truth_surfaces")
    registry = module.build_backend_truth_surface_registry(tmp_path)

    assert registry["backend_owns_truth"] is True
    assert registry["cockpit_presentation_only"] is True
    assert registry["runtime_truth_mutation_allowed"] is False
    assert registry["automatic_update_allowed"] is False
    assert registry["surface_count"] == 9
    assert len(registry["registry_sha256"]) == 64


def test_s40r2_status_reports_surfaces_without_mutation(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_backend_truth_surfaces")
    make_plateau(tmp_path)
    status = module.build_backend_truth_surface_status(tmp_path)

    assert status["surfaces"]["manual_promotion_status"]["available"] is True
    assert status["surfaces"]["update_proposal_status"]["available"] is True
    assert status["runtime_truth_mutation_allowed"] is False
    assert status["automatic_update_allowed"] is False
    assert len(status["status_sha256"]) == 64


def test_s40r3_payload_includes_manual_promotion_read_only(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_backend_truth_surfaces")
    make_plateau(tmp_path)
    payload = module.build_backend_truth_surface_payload(tmp_path)

    assert payload["backend_owns_truth"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["manual_promotion"]["plateau_report"]["available"] is True
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["browser_execution_allowed"] is False
    assert payload["javascript_execution_allowed"] is False
    assert len(payload["payload_sha256"]) == 64


def test_s40r4_writes_backend_truth_surface_files(tmp_path: Path):
    module = importlib.import_module("claire.api.governed_backend_truth_surfaces")
    make_plateau(tmp_path)
    result = module.write_backend_truth_surface_payload(tmp_path, tmp_path / "out")

    assert set(result) == {"registry", "status", "payload"}
    for value in result.values():
        assert Path(value).exists()

    payload = json.loads(Path(result["payload"]).read_text(encoding="utf-8"))
    assert payload["runtime_truth_mutation_allowed"] is False
    assert payload["automatic_update_allowed"] is False
