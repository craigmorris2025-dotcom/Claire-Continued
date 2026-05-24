from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from runtime_core.design.artifact_package import build_design_artifact_package, execute_design_portal_action


def test_dashboard_state_exposes_live_design_portal_workbench():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    portal = payload["design_portal_workbench"]
    assert portal["schema_version"] == "claire_live_design_portal_v1"
    assert portal["mode"] == "live_system_design_workbench"
    assert portal["status"] in {"preview_ready", "insufficient_design_context"}
    assert portal["candidate"]["title"]
    assert portal["architecture"]["nodes"]
    assert portal["required_components"]
    assert portal["required_systems"]
    assert portal["materials_manifest"]["technology_materials"]
    assert portal["materials_manifest"]["component_materials"]
    assert portal["materials_manifest"]["code_materials"]
    assert portal["blueprint_package"]["exports_required"]
    assert portal["invention_commitment"]["status"] in {"commit_candidate_ready", "needs_more_validation"}
    assert isinstance(portal["invention_commitment"]["commit_to_build_attempt"], bool)
    assert portal["downstream_route_contract"]["portfolio_required"] is True
    assert portal["downstream_route_contract"]["acquirer_matching_required"] is True
    assert portal["downstream_route_contract"]["package_required"] is True
    assert portal["artifact_package"]["status"] == "design_artifact_package_ready"
    assert portal["artifact_package"]["cad_viewer_required"] is True
    assert portal["artifact_package"]["video_viewer_required"] is True
    assert portal["artifact_package"]["runtime_truth_mutation"] is False
    assert portal["runtime_design_alert"]["status"] in {"active", "watching"}
    assert portal["runtime_design_alert"]["opens_surface"] == "design_portal"
    assert portal["portal_actions"]
    assert {item["id"] for item in portal["portal_actions"]} >= {
        "prepare_cad_viewer",
        "prepare_video_viewer",
        "prepare_asset_import_slots",
        "hold_design_package",
        "approve_design_package",
        "validate_design_route",
    }
    assert portal["validation_chain"]["completion_percent"] == 100
    assert portal["live_design_events"]
    assert portal["promotion_gates"]
    assert isinstance(portal["buildability"]["current_tech_compatible"], bool)
    assert portal["buildability"]["sci_fi_risk"] in {"low", "medium", "high"}
    assert "ready" in portal["blueprint_readiness"]
    assert portal["authority"]["runtime_truth_mutation"] is False
    assert portal["authority"]["manual_promotion_required"] is True
    current = payload["current_run_truth"]
    if current["run_id"]:
        assert portal["candidate"]["source_run_id"] == current["run_id"]


def test_design_artifact_package_writes_core_files():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    package = payload["design_artifact_package"]
    package_dir = Path(package["package_dir"])
    assert package_dir.exists()
    for filename in [
        "manifest.json",
        "blueprint_package.json",
        "materials_manifest.json",
        "component_map.json",
        "cad_artifact_registry.json",
        "video_simulation_registry.json",
        "downstream_route_handoff.json",
        "README.md",
    ]:
        assert (package_dir / filename).exists()
    assert package["cad_viewer_required"] is True
    assert package["video_viewer_required"] is True
    assert package["manual_review_required"] is True


def test_design_portal_action_endpoints_prepare_viewers_and_validate_route():
    client = TestClient(app)

    actions = client.get("/api/dashboard/state").json()["design_portal_workbench"]
    assert actions["runtime_design_alert"]["opens_surface"] == "design_portal"

    cad = client.post("/api/cockpit/command/plan", json={"intent": "design_portal_action", "action_id": "prepare_cad_viewer"}).json()
    video = client.post("/api/cockpit/command/plan", json={"intent": "design_portal_action", "action_id": "prepare_video_viewer"}).json()
    slots = client.post("/api/cockpit/command/plan", json={"intent": "design_portal_action", "action_id": "prepare_asset_import_slots"}).json()
    route = client.post("/api/cockpit/command/plan", json={"intent": "design_portal_action", "action_id": "validate_design_route"}).json()
    promote = client.post("/api/cockpit/command/plan", json={"intent": "design_portal_action", "action_id": "promote_design_package"}).json()

    assert cad["status"] == "recorded"
    assert cad["result"]["viewer"]["status"] == "ready_waiting_for_asset"
    assert video["result"]["viewer"]["status"] == "ready_waiting_for_asset"
    assert slots["result"]["cad_import_slots_ready"] is True
    assert route["status"] == "route_validated"
    assert route["result"]["validation_chain"]["completion_percent"] == 100
    assert promote["status"] in {"blocked", "promoted_for_downstream_review"}
    assert promote["runtime_truth_mutation"] is False
    if promote["status"] == "promoted_for_downstream_review":
        assert promote["result"]["body_read_performed"] is False
        assert promote["result"]["runtime_truth_mutation"] is False
    else:
        assert promote["result"]["reason"] == "promotion_requires_live_evidence_and_explicit_operator_promotion_gate"


def test_design_package_promotion_opens_only_after_promoted_live_metadata(tmp_path):
    workbench = {
        "candidate": {"title": "Governed package candidate", "source_run_id": "cycle_live_proof"},
        "blueprint_package": {"status": "ready"},
        "materials_manifest": {"status": "ready"},
        "validation_chain": {"status": "validated", "completion_percent": 100},
    }
    build_design_artifact_package(workbench, tmp_path)

    blocked = execute_design_portal_action("promote_design_package", tmp_path)
    assert blocked["status"] == "blocked"
    assert blocked["result"]["live_evidence"]["metadata_evidence_count"] == 0
    assert blocked["runtime_truth_mutation"] is False

    evidence_path = tmp_path / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": "v19.89.8_promoted_metadata_evidence_store",
                "status": "ready",
                "items": [
                    {
                        "evidence_id": "evidence-connected-meta-test",
                        "provider": "brave",
                        "metadata_only": True,
                        "body_read_performed": False,
                        "runtime_truth_write": "blocked",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    promoted = execute_design_portal_action("promote_design_package", tmp_path, operator_note="approved proof run")
    assert promoted["status"] == "promoted_for_downstream_review"
    assert promoted["blocked"] is False
    assert promoted["result"]["live_evidence"]["providers"] == ["brave"]
    assert promoted["result"]["body_read_performed"] is False
    assert promoted["runtime_truth_mutation"] is False


def test_design_portal_lists_core_runtime_components_needed_to_function():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    component_ids = {item["id"] for item in payload["design_portal_workbench"]["required_components"]}
    assert {"ingestion", "semantic_processing", "analysis_engines", "decision_layer", "api_gateway"} <= component_ids


def test_dashboard_renders_operator_design_portal_surface():
    root = Path(__file__).resolve().parents[1]
    js = (root / "frontend" / "command_center" / "modern" / "platform_dashboard.js").read_text(encoding="utf-8")

    assert "Design Portal" in js
    assert "renderDesignPortal" in js
    assert "Live Design Workbench" in js
    assert "Required Components" in js
    assert "Materials, Code, and Systems Needed" in js
    assert "Blueprint and Route Contract" in js
    assert "Artifact Package" in js
    assert "CAD viewer" in js
    assert "Video viewer" in js
    assert "Design Asset Viewer Surface" in js
    assert "cad-viewer-pane" in js
    assert "video-viewer-pane" in js
    assert "Breakthrough / Discovery Design Alert" in js
    assert "Portal Functions" in js
    assert "Route Validation Chain" in js
    assert "runDesignPortalAction" in js
    assert "Current-tech compatible" in js
    assert "Sci-fi risk" in js


def test_dashboard_exposes_post_run_output_handoff():
    client = TestClient(app)
    payload = client.get("/api/dashboard/state").json()

    handoff = payload["post_run_handoff"]
    assert handoff["schema_version"] == "claire.post_run_handoff.v1"
    assert handoff["run_id"] == payload["current_run_truth"]["run_id"]
    assert handoff["route_selected"] == payload["current_run_truth"]["route_selected"]
    assert handoff["output_locations"]["portfolio_view_url"]
    assert handoff["output_locations"]["portfolio_download_url"]
    assert handoff["output_locations"]["review_queue"] == "data/continuous_runtime/review_queue.json"
    assert handoff["route_gates"]["design"]["status"] == payload["current_run_truth"]["design_gate"]["status"]
    assert handoff["if_technology_scores"]["dashboard_surface"] == "Design Portal"
    assert "final business/acquisition package" in handoff["if_technology_scores"]["downstream_after_design"]
    assert handoff["next_actions"]

    root = Path(__file__).resolve().parents[1]
    js = (root / "frontend" / "command_center" / "modern" / "platform_dashboard.js").read_text(encoding="utf-8")
    assert "Post-Run Output Handoff" in js
    assert "Open Portfolio" in js
    assert "If technology scores" in js
