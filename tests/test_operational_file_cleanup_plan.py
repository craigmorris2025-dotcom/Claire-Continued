from __future__ import annotations

from fastapi.testclient import TestClient


def test_operational_file_readiness_exposes_review_only_cleanup_plan():
    from runtime_core.app import create_app

    client = TestClient(create_app())
    payload = client.get("/api/system/file-readiness").json()

    cleanup_plan = payload["cleanup_plan"]
    assert cleanup_plan["delete_allowed"] is False
    assert cleanup_plan["archive_execution_allowed"] is False
    assert cleanup_plan["operator_review_required"] is True
    assert cleanup_plan["destructive_cleanup_performed"] is False
    assert cleanup_plan["archive_plan_path"] == "data/cleanup/archive_plan_do_not_execute.json"
