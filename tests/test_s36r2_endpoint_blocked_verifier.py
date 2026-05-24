from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest
from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[1]


def _module():
    return importlib.import_module("runtime_core.api.routes.governed_live_probe")


def test_s36r2_status_contract_is_blocked_by_default(monkeypatch):
    module = _module()
    for key in [
        "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE",
        "PLATFORM_ALLOW_HEAD_ONLY_PROBE",
        "PLATFORM_ALLOW_RESPONSE_BODY_READ",
        "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION",
        "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION",
    ]:
        monkeypatch.delenv(key, raising=False)

    status = module.governed_live_probe_status()
    assert status["registered"] is True
    assert status["operator_triggered_only"] is True
    assert status["one_shot_only"] is True
    assert status["method_allowed"] == "HEAD"
    assert status["body_reads_allowed"] is False
    assert status["browser_execution_allowed"] is False
    assert status["runtime_truth_mutation_allowed"] is False
    assert status["autonomous_execution_allowed"] is False
    assert status["provider_gate_enabled"] is False
    assert status["head_gate_enabled"] is False


def test_s36r2_probe_rejects_when_provider_gates_disabled(monkeypatch):
    module = _module()
    for key in [
        "PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE",
        "PLATFORM_ALLOW_HEAD_ONLY_PROBE",
        "PLATFORM_ALLOW_RESPONSE_BODY_READ",
        "PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION",
        "PLATFORM_ALLOW_AUTONOMOUS_EXECUTION",
    ]:
        monkeypatch.delenv(key, raising=False)

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=True, one_shot=True)
    with pytest.raises(HTTPException) as exc:
        module._assert_execution_allowed(payload)
    assert exc.value.status_code == 403
    assert "provider gate is disabled" in str(exc.value.detail)


def test_s36r2_probe_rejects_missing_operator_ack_even_if_gates_enabled(monkeypatch):
    module = _module()
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=False, one_shot=True)
    with pytest.raises(HTTPException) as exc:
        module._assert_execution_allowed(payload)
    assert exc.value.status_code == 403
    assert "Operator acknowledgement required" in str(exc.value.detail)


def test_s36r2_probe_rejects_body_read_authority(monkeypatch):
    module = _module()
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=True, one_shot=True)
    with pytest.raises(HTTPException) as exc:
        module._assert_execution_allowed(payload)
    assert exc.value.status_code == 403
    assert "Body-read authority must remain disabled" in str(exc.value.detail)


def test_s36r2_probe_rejects_runtime_mutation_authority(monkeypatch):
    module = _module()
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.setenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=True, one_shot=True)
    with pytest.raises(HTTPException) as exc:
        module._assert_execution_allowed(payload)
    assert exc.value.status_code == 403
    assert "Runtime truth mutation must remain disabled" in str(exc.value.detail)


def test_s36r2_probe_rejects_autonomous_execution_authority(monkeypatch):
    module = _module()
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.setenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", "1")

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=True, one_shot=True)
    with pytest.raises(HTTPException) as exc:
        module._assert_execution_allowed(payload)
    assert exc.value.status_code == 403
    assert "Autonomous execution must remain disabled" in str(exc.value.detail)


def test_s36r2_gates_pass_only_for_operator_one_shot_head_metadata(monkeypatch):
    module = _module()
    monkeypatch.setenv("PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE", "1")
    monkeypatch.setenv("PLATFORM_ALLOW_HEAD_ONLY_PROBE", "1")
    monkeypatch.delenv("PLATFORM_ALLOW_RESPONSE_BODY_READ", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", raising=False)
    monkeypatch.delenv("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", raising=False)

    payload = module.HeadProbeRequest(url="https://example.com", operator_ack=True, one_shot=True)
    assert module._assert_execution_allowed(payload) is None
