
from __future__ import annotations

import importlib
import json
from pathlib import Path


def sample_snapshot():
    return {
        "operator_state_snapshot_sha256": "s" * 64,
        "section_count": 3,
        "available_section_count": 2,
        "unavailable_section_count": 1,
        "unavailable_sections": [
            {"section": "research_queue", "reason": "missing", "path": "output/q"}
        ],
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
    }


def sample_summary():
    return {
        "bounded_runtime_summary_sha256": "b" * 64,
        "status": "partial_surfaces_available",
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
    }


def test_s41r5_builds_current_state_digest():
    module = importlib.import_module("runtime_core.api.governed_operator_state_digest")
    digest = module.build_current_state_digest(sample_snapshot(), sample_summary())

    assert digest["state"] == "partial"
    assert digest["backend_owns_truth"] is True
    assert digest["cockpit_presentation_only"] is True
    assert digest["runtime_truth_mutation_allowed"] is False
    assert digest["automatic_update_allowed"] is False
    assert len(digest["current_state_digest_sha256"]) == 64


def test_s41r6_builds_operator_alert_summary():
    module = importlib.import_module("runtime_core.api.governed_operator_state_digest")
    digest = module.build_current_state_digest(sample_snapshot(), sample_summary())
    alerts = module.build_operator_alert_summary(sample_snapshot(), digest)

    assert alerts["alert_count"] == 1
    assert alerts["alerts"][0]["code"] == "surface_unavailable"
    assert alerts["runtime_truth_mutation_allowed"] is False
    assert alerts["automatic_update_allowed"] is False


def test_s41r7_replay_index_and_readiness_are_locked():
    module = importlib.import_module("runtime_core.api.governed_operator_state_digest")
    digest = module.build_current_state_digest(sample_snapshot(), sample_summary())
    alerts = module.build_operator_alert_summary(sample_snapshot(), digest)
    replay = module.build_snapshot_replay_index(sample_snapshot(), sample_summary(), digest, alerts)
    readiness = module.build_s41_readiness_report(digest, alerts, replay)

    assert replay["digest_sha256"] == digest["current_state_digest_sha256"]
    assert readiness["status"] == "s41_ready"
    assert readiness["runtime_truth_mutation_allowed"] is False
    assert readiness["automatic_update_allowed"] is False


def test_s41r8_writes_and_verifies_digest_artifacts(tmp_path: Path):
    module = importlib.import_module("runtime_core.api.governed_operator_state_digest")
    source = tmp_path / "output" / "operator_runtime_snapshots"
    source.mkdir(parents=True)
    (source / "operator_state_snapshot.json").write_text(json.dumps(sample_snapshot()), encoding="utf-8")
    (source / "bounded_runtime_summary.json").write_text(json.dumps(sample_summary()), encoding="utf-8")

    result = module.write_s41_operator_state_digest(tmp_path, tmp_path / "out")
    assert set(result) == {"digest", "alerts", "replay_index", "readiness", "verification"}
    for value in result.values():
        assert Path(value).exists()

    verification = json.loads(Path(result["verification"]).read_text(encoding="utf-8"))
    assert verification["verification_ok"] is True
