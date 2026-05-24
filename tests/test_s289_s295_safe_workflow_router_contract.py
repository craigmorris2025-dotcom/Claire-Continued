from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_s289_s295_safe_workflow_router_contract():
    from runtime_core.api.safe_workflow_routes import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    counts = client.get("/api/workflow/counts")
    assert counts.status_code == 200
    payload = counts.json()
    assert payload["ok"] is True
    assert payload["authority_locks"]["runtime_truth_write_allowed"] is False
    assert payload["authority_locks"]["runtime_mutation_allowed"] is False
    assert payload["authority_locks"]["automatic_updates_allowed"] is False
    assert payload["authority_locks"]["autonomous_execution_allowed"] is False
    assert payload["authority_locks"]["continuous_crawling_allowed"] is False
    assert payload["authority_locks"]["workflow_actions_mode"] == "proposal_only"
    assert "review_queue_total" in payload["counts"]
    assert "bounded_jobs_total" in payload["counts"]
    assert "exports_total" in payload["counts"]
    assert "audit_events_total" in payload["counts"]

    job = client.post("/api/workflow/bounded-job", json={"job_type": "test", "max_items": 1})
    assert job.status_code == 200
    job_payload = job.json()
    assert job_payload["state"] == "job_proposal_recorded"
    assert job_payload["runtime_mutation_started"] is False
    assert job_payload["autonomous_execution_started"] is False

    decision = client.post("/api/workflow/review-decision", json={"item_id": "x", "decision": "hold"})
    assert decision.status_code == 200
    decision_payload = decision.json()
    assert decision_payload["proposal_only"] is True
    assert decision_payload["runtime_truth_modified"] is False

    export = client.post("/api/workflow/export", json={"export_type": "pytest_snapshot"})
    assert export.status_code == 200
    export_payload = export.json()
    assert export_payload["state"] == "export_artifact_written"
    assert export_payload["runtime_truth_modified"] is False

    monitoring = client.get("/api/workflow/monitoring")
    assert monitoring.status_code == 200
    monitoring_payload = monitoring.json()
    assert monitoring_payload["live_refresh_supported"] is True
    assert monitoring_payload["refresh_interval_ms"] == 15000
