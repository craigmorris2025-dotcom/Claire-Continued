from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from runtime_core.app import create_app
from runtime_core.api.dependency_chain_proof import build_dependency_chain_proof


def test_dependency_chain_proof_runs_clean_against_mounted_app():
    client = TestClient(create_app())

    payload = client.get("/api/system/dependency-chain-proof").json()

    assert payload["schema_version"] == "claire.dependency_chain_proof.v1"
    assert payload["status"] == "clean_e2e_review_proof"
    assert payload["mounted_missing"] == []
    assert payload["blocked_steps"] == []
    assert payload["blocked_edges"] == []
    assert payload["passed_step_count"] == payload["step_count"]
    assert payload["boundaries"]["cad_export_enabled"] is False
    assert payload["boundaries"]["automatic_update_apply_enabled"] is False


def test_dependency_chain_proof_contains_no_ambiguous_owner_handoffs():
    payload = build_dependency_chain_proof(create_app())

    for step in payload["steps"]:
        assert step["owner"].startswith("runtime_core.")
        assert step["endpoint"].startswith("/")
        assert step["handoff_fields"]
        assert step["status"] == "passed"

    edges = payload["handoff_edges"]
    assert edges
    assert all(edge["status"] == "passed" for edge in edges)


def test_dependency_chain_proof_writes_review_artifacts(tmp_path: Path):
    payload = build_dependency_chain_proof(create_app(), project_root=tmp_path)

    assert payload["status"] == "clean_e2e_review_proof"
    assert (tmp_path / "data" / "proof" / "dependency_to_dependency_e2e_proof.json").exists()
    assert (tmp_path / "docs" / "engineering" / "dependency_to_dependency_e2e_proof.md").exists()
