from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from runtime_core.app import create_app
from runtime_core.platform.update_governance.open_web_update_governance import (
    APPROVAL_PHRASE,
    apply_governed_update,
    build_open_web_readiness_report,
    build_install_readiness,
    build_self_analysis,
    create_update_request,
    evaluate_update_candidate,
    stage_update_install,
    stable_digest,
)


def signed_candidate(**overrides):
    candidate = {
        "update_id": "open_web_update_test",
        "provider_id": "local_operator",
        "package_uri": "file:///tmp/open-web-update.json",
        "version_from": "rc1",
        "version_to": "open-web-rc2",
        "capabilities": ["provider_gate", "approval_workflow", "rollback_plan"],
        "target_paths": ["claire/api/routes_open_web_update_governance.py"],
        "metadata": {"summary": "governed metadata-only update proposal"},
    }
    candidate.update(overrides)
    digest_payload = {
        "update_id": candidate.get("update_id"),
        "provider_id": candidate.get("provider_id"),
        "version_from": candidate.get("version_from"),
        "version_to": candidate.get("version_to"),
        "capabilities": candidate.get("capabilities") or [],
        "target_paths": candidate.get("target_paths") or [],
        "metadata": candidate.get("metadata"),
    }
    digest = stable_digest(digest_payload)
    candidate["expected_sha256"] = digest
    candidate["signature"] = f"sha256:{digest}"
    return candidate


def test_open_web_provider_signature_approval_and_rollback_contract():
    evaluation = evaluate_update_candidate(signed_candidate())

    assert evaluation["status"] == "approval_required"
    assert evaluation["provider_gate"]["trusted"] is True
    assert evaluation["signature_verification"]["verified"] is True
    assert evaluation["approval_workflow"]["approval_required"] is True
    assert evaluation["rollback"]["rollback_required"] is True
    assert evaluation["install_allowed"] is False
    assert evaluation["install_performed"] is False
    assert evaluation["runtime_mutation_allowed"] is False


def test_unapproved_external_provider_is_blocked():
    evaluation = evaluate_update_candidate(
        signed_candidate(
            provider_id="unknown_external",
            package_uri="https://updates.example.com/update.json",
        )
    )

    assert evaluation["status"] == "blocked"
    assert evaluation["provider_gate"]["trusted"] is False
    assert "provider_trust_failed" in evaluation["blockers"]
    assert evaluation["download_allowed"] is False


def test_runtime_truth_firewall_blocks_protected_core_paths():
    evaluation = evaluate_update_candidate(
        signed_candidate(target_paths=["claire/runtime_truth/core_policy.py"])
    )

    assert evaluation["status"] == "blocked"
    assert "protected_core_logic_target_requires_owner_approval" in evaluation["blockers"]
    assert evaluation["runtime_truth_firewall"]["runtime_truth_mutation_allowed"] is False
    assert evaluation["runtime_truth_firewall"]["external_mutation_performed"] is False


def test_self_analysis_requests_missing_capabilities_without_self_mutation():
    analysis = build_self_analysis(
        required_capabilities=["provider_gate", "signature_verification", "rollback"],
        available_capabilities=["provider_gate"],
    )

    assert analysis["status"] == "capability_gaps_detected"
    assert analysis["missing_capabilities"] == ["signature_verification", "rollback"]
    assert all(item["approval_required"] for item in analysis["update_requests"])
    assert analysis["self_mutation_allowed"] is False


def test_update_request_writes_audit_and_proposal_only_records(tmp_path: Path):
    result = create_update_request(signed_candidate(), project_root=tmp_path)

    assert result["request_recorded"] is True
    assert Path(result["request_path"]).exists()
    assert Path(result["audit"]["audit_path"]).exists()
    assert result["approval_workflow"]["approval_applies_update"] is False
    assert result["install_performed"] is False


def test_update_install_workflow_requires_approval_package_and_writes_rollback(tmp_path: Path):
    candidate = signed_candidate(
        target_paths=["sandbox_target.py"],
        files={"sandbox_target.py": "VALUE = 'updated'\n"},
    )
    target = tmp_path / "sandbox_target.py"
    target.write_text("VALUE = 'original'\n", encoding="utf-8")
    create_update_request(candidate, project_root=tmp_path)

    unapproved = build_install_readiness("open_web_update_test", project_root=tmp_path)
    assert unapproved["install_allowed"] is False
    assert "owner_approval_missing" in unapproved["blockers"]

    approved = client_result = apply_governed_update("open_web_update_test", APPROVAL_PHRASE, project_root=tmp_path)
    assert client_result["status"] == "install_applied"
    assert approved["install_performed"] is True
    assert target.read_text(encoding="utf-8") == "VALUE = 'updated'\n"
    assert Path(approved["rollback_path"]).exists()


def test_update_install_stage_explains_missing_package_payload(tmp_path: Path):
    create_update_request(signed_candidate(target_paths=["sandbox_target.py"]), project_root=tmp_path)
    from runtime_core.platform.update_governance.open_web_update_governance import record_user_approval

    record_user_approval("open_web_update_test", APPROVAL_PHRASE, project_root=tmp_path)
    staged = stage_update_install("open_web_update_test", project_root=tmp_path)
    assert staged["install_allowed"] is False
    assert "package_payload_missing" in staged["blockers"]


def test_open_web_readiness_report_declares_governed_ready():
    report = build_open_web_readiness_report()

    assert report["ready"] is True
    assert report["status"] == "open_web_ready_governed_mode"
    assert report["checks"]["provider_gate_available"] is True
    assert report["checks"]["automatic_updates_disabled"] is True
    assert report["dashboard_update_panel"]["security_posture"]["privileged_surfaces_exposed"] is False
    assert report["dashboard_update_panel"]["install_workflow"]["install_endpoints_exposed"] is True


def test_open_web_update_governance_api_routes_are_mounted_and_safe(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = TestClient(create_app())

    readiness = client.get("/api/update-governance/open-web/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["ready"] is True

    blocked = client.post("/api/update-governance/open-web/request", json=signed_candidate(package_uri="https://unapproved.example/update.json"))
    assert blocked.status_code == 409
    assert blocked.json()["install_performed"] is False
    assert "provider_trust_failed" in blocked.json()["blockers"]

    approval_rejected = client.post(
        "/api/update-governance/open-web/approve",
        json={"update_id": "open_web_update_test", "approval_phrase": "yes"},
    )
    assert approval_rejected.status_code == 403
    assert approval_rejected.json()["install_performed"] is False

    approval_recorded = client.post(
        "/api/update-governance/open-web/approve",
        json={"update_id": "open_web_update_test", "approval_phrase": APPROVAL_PHRASE},
    )
    assert approval_recorded.status_code == 202
    assert approval_recorded.json()["user_approved"] is True
    assert approval_recorded.json()["approval_applies_update"] is False
    assert approval_recorded.json()["runtime_mutation_performed"] is False

    install_status = client.get("/api/update-governance/open-web/install/status/open_web_update_test")
    assert install_status.status_code == 200
    assert install_status.json()["install_endpoint"] == "/api/update-governance/open-web/install/apply"

    staged = client.post(
        "/api/update-governance/open-web/install/stage",
        json={"update_id": "open_web_update_test"},
    )
    assert staged.status_code == 409
    assert staged.json()["install_performed"] is False
