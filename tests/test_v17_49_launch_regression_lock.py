from __future__ import annotations

import json
from pathlib import Path

from claire.governance.launch_regression_lock import LaunchRegressionLock, LaunchRegressionLockError, run_launch_regression_lock
from claire.governance.launch_release_gate import LaunchReleaseGate
from claire.governance.launch_contract_freeze import freeze_contract


def test_v17_49_lock_passes_with_default_launch_config():
    cert = run_launch_regression_lock(Path.cwd(), {
        "runtime_isolation": "enforced",
        "max_orchestration_depth": 8,
        "max_runtime_seconds": 900,
        "max_concurrent_campaigns": 4,
    })
    assert cert["version"] == "v17.49"
    assert cert["passed"] is True
    assert cert["release_blocked"] is False
    assert cert["invariant_hash"]
    assert len(cert["checks"]) >= 10


def test_launch_gate_allows_when_regression_lock_passes():
    gate = LaunchReleaseGate(Path.cwd())
    decision = gate.evaluate({"runtime_isolation": "strict"})
    assert decision.allowed is True
    assert decision.status == "launch_allowed"
    assert Path(decision.certificate_path).exists()


def test_launch_gate_blocks_forbidden_runtime_flag():
    gate = LaunchReleaseGate(Path.cwd())
    decision = gate.evaluate({"disable_governance": True})
    assert decision.allowed is False
    assert decision.status == "launch_blocked"
    assert "forbidden_runtime_flags" in decision.reason


def test_orchestration_bounds_are_enforced():
    lock = LaunchRegressionLock(Path.cwd())
    cert = lock.run_all({"max_orchestration_depth": 99, "max_runtime_seconds": 9999, "max_concurrent_campaigns": 99})
    failed = [check.name for check in cert.checks if not check.passed]
    assert "orchestration_bounds" in failed
    assert cert.release_blocked is True


def test_contract_freeze_digest_is_stable():
    first = freeze_contract("runtime_contract", "v17.49", {"b": 2, "a": 1})
    second = freeze_contract("runtime_contract", "v17.49", {"a": 1, "b": 2})
    assert first.digest == second.digest
    assert first.name == "runtime_contract"


def test_certificate_file_is_written():
    lock = LaunchRegressionLock(Path.cwd())
    cert = lock.run_all({})
    path = lock.write_certificate(cert)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == "v17.49"
    assert "checks" in data
