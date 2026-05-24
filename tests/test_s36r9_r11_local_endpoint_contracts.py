from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]


def _client():
    from runtime_core.app import create_app

    return TestClient(create_app())


def test_s36r9_status_endpoint_visible_and_safe():
    client = _client()
    response = client.get("/api/governed/live-probe/status")
    assert response.status_code == 200
    data = response.json()
    assert data["registered"] is True
    assert data["operator_triggered_only"] is True
    assert data["one_shot_only"] is True
    assert data["method_allowed"] == "HEAD"
    assert data["body_reads_allowed"] is False
    assert data["browser_execution_allowed"] is False
    assert data["runtime_truth_mutation_allowed"] is False
    assert data["autonomous_execution_allowed"] is False


def test_s36r10_post_head_endpoint_blocked_by_default(monkeypatch):
    for key in [
        "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE",
        "PLATFORM_ALLOW_HEAD_ONLY_PROBE",
        "PLATFORM_ALLOW_RESPONSE_BODY_READ",
        "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION",
        "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION",
    ]:
        monkeypatch.delenv(key, raising=False)

    client = _client()
    response = client.post(
        "/api/governed/live-probe/head",
        json={
            "url": "https://example.com",
            "operator_ack": True,
            "one_shot": True,
        },
    )
    assert response.status_code == 403
    assert "provider gate is disabled" in response.text


def test_s36r10_post_head_endpoint_requires_operator_ack(monkeypatch):
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    client = _client()
    response = client.post(
        "/api/governed/live-probe/head",
        json={
            "url": "https://example.com",
            "operator_ack": False,
            "one_shot": True,
        },
    )
    assert response.status_code == 403
    assert "Operator acknowledgement required" in response.text


def test_s36r10_post_head_endpoint_rejects_non_one_shot(monkeypatch):
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    client = _client()
    response = client.post(
        "/api/governed/live-probe/head",
        json={
            "url": "https://example.com",
            "operator_ack": True,
            "one_shot": False,
        },
    )
    assert response.status_code == 403
    assert "Only one-shot execution is allowed" in response.text


def test_s36r11_operator_probe_pack_files_exist():
    op = ROOT / "tools" / "run_s36_single_head_probe.py"
    verify = ROOT / "tools" / "verify_s36_probe_quarantine.py"
    assert op.exists()
    assert verify.exists()

    op_source = op.read_text(encoding="utf-8")
    assert "--operator-ack" in op_source
    assert 'choices=["YES"]' in op_source
    assert "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE" in op_source
    assert "PLATFORM_ALLOW_HEAD_ONLY_PROBE" in op_source

    verify_source = verify.read_text(encoding="utf-8")
    assert "last_single_head_probe_manifest.json" in verify_source
    assert "manual_promotion_required" in verify_source
    assert "HEAD_METADATA_ONLY" in verify_source


def test_s36r11_no_live_probe_manifest_created_by_installs():
    request_manifest = ROOT / "runtime" / "governed_live_probe" / "operator_single_head_probe_request.json"
    # It is okay if the user already manually ran a probe. The install itself must not create a fresh forced command.
    if request_manifest.exists():
        data = json.loads(request_manifest.read_text(encoding="utf-8"))
        assert data.get("operator_ack") is True
        assert data.get("one_shot_only") is True
        assert data.get("method") == "HEAD"
        assert data.get("body_read") is False
