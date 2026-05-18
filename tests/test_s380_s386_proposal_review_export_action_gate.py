from __future__ import annotations
from fastapi import FastAPI
from fastapi.testclient import TestClient
from claire.api.internet_proposal_review_export_action_s380_s386 import (
    build_proposal_review_export_action_gate_s380_s386, build_s380_proposal_action_authority,
    build_s381_review_action_request_contract, build_s384_dashboard_action_registry_review_export_enabled,
    build_s385_route_registration_proof, build_s386_stop_gate, execute_s382_review_action,
    execute_s383_export_action, register_s380_s386_proposal_review_export_routes,
)

def test_s380_proposal_action_authority_blocks_runtime_write():
    p=build_s380_proposal_action_authority(); a=p["action_authority"]
    assert p["stage_version"]=="S380"; assert a["export_allowed"] is True; assert a["runtime_truth_write_allowed"] is False; assert a["self_apply_allowed"] is False

def test_s381_review_action_contract_accepts_export_only():
    p=build_s381_review_action_request_contract("export_only")
    assert p["stage_version"]=="S381"; assert p["request_contract"]["allowed"] is True

def test_s382_review_action_records_proposal_only():
    p=execute_s382_review_action({"action":"export_only","operator_confirmed":True}); d=p["review_decision"]
    assert p["stage_version"]=="S382"; assert d["status"]=="recorded_proposal_only"; assert d["runtime_truth_modified"] is False

def test_s383_export_action_writes_export_files(tmp_path, monkeypatch):
    import claire.api.internet_proposal_review_export_action_s380_s386 as module
    monkeypatch.setattr(module, "EXPORT_DIR", tmp_path)
    p=module.execute_s383_export_action({"operator_confirmed":True})
    assert p["stage_version"]=="S383"; assert p["export_authorized"] is True; assert p["runtime_truth_modified"] is False; assert p["export_paths"]

def test_s384_dashboard_actions_enabled_but_runtime_write_blocked():
    p=build_s384_dashboard_action_registry_review_export_enabled(); actions=p["action_registry_patch"]
    assert p["stage_version"]=="S384"; assert actions["approve_proposal"]["enabled"] is True
    assert actions["approve_proposal"]["runtime_truth_write_enabled"] is False; assert actions["export_proposal"]["enabled"] is True

def test_s385_routes_registered():
    p=build_s385_route_registration_proof()
    assert p["stage_version"]=="S385"; assert p["review_route_registered"] is True; assert p["export_route_registered"] is True; assert p["status_route_registered"] is True

def test_s385_proposal_routes_work_with_testclient(tmp_path, monkeypatch):
    import claire.api.internet_proposal_review_export_action_s380_s386 as module
    monkeypatch.setattr(module, "EXPORT_DIR", tmp_path)
    app=FastAPI(); module.register_s380_s386_proposal_review_export_routes(app); client=TestClient(app)
    review=client.post("/api/internet/proposals/review", json={"action":"export_only","operator_confirmed":True})
    assert review.status_code==200; assert review.json()["review_decision"]["status"]=="recorded_proposal_only"
    export=client.post("/api/internet/proposals/export", json={"operator_confirmed":True})
    assert export.status_code==200; assert export.json()["export_authorized"] is True
    status=client.get("/api/internet/proposals/status")
    assert status.status_code==200; assert status.json()["proposal_review_export_enabled"] is True

def test_s386_stop_gate_passes(tmp_path, monkeypatch):
    import claire.api.internet_proposal_review_export_action_s380_s386 as module
    monkeypatch.setattr(module, "EXPORT_DIR", tmp_path / "exports")
    p=build_s386_stop_gate(report_dir=tmp_path)
    assert p["stage_version"]=="S386"; assert p["forward_motion_allowed"] is True; assert p["checks"]["runtime_truth_not_modified"] is True; assert "report_path" in p

def test_s380_s386_rollup_ready():
    p=build_proposal_review_export_action_gate_s380_s386()
    assert p["stage_version"]=="S386"; assert p["stop_gate"]["forward_motion_allowed"] is True
