from __future__ import annotations

import json
from pathlib import Path

import pytest

from claire.deployment import (
    DeploymentReadinessValidator,
    NetworkExposureValidator,
    ProductionHealthContract,
    ProductionProfileError,
    RuntimeHardeningValidator,
    SecretScanner,
    load_production_profile,
)


def test_production_profile_accepts_safe_defaults():
    profile = load_production_profile(env={})
    assert profile.environment == "production"
    assert profile.debug is False
    assert profile.allow_unbounded_orchestration is False
    assert profile.allow_runtime_mutation is False
    assert profile.max_retry_attempts == 3


def test_production_profile_rejects_debug_mode():
    with pytest.raises(ProductionProfileError):
        load_production_profile(env={"CLAIRE_DEBUG": "true"})


def test_runtime_hardening_requires_launch_critical_capabilities():
    validator = RuntimeHardeningValidator()
    findings = validator.validate_capabilities(
        {
            "governed_external_search",
            "persistent_campaigns",
            "campaign_scheduler",
            "runtime_recovery",
            "adaptive_source_trust",
            "source_quarantine",
            "operations_dashboard",
            "bounded_orchestration",
            "rollback_safety",
            "runtime_isolation",
        }
    )
    assert findings == []


def test_runtime_hardening_reports_missing_capability():
    validator = RuntimeHardeningValidator()
    findings = validator.validate_capabilities({"governed_external_search"})
    assert any("persistent_campaigns" in item for item in findings)


def test_secret_scanner_detects_secret_assignment():
    scanner = SecretScanner()
    findings = scanner.scan_text("api_key = 'abcdefghijklmnopqrstuvwxyz'", path="sample.py")
    assert findings
    assert findings[0].pattern_name == "generic_secret_assignment"


def test_network_policy_rejects_wildcard_cors():
    validator = NetworkExposureValidator()
    findings = validator.validate_cors_origins(["*"])
    assert findings


def test_health_contract_ready_status():
    contract = ProductionHealthContract()
    status = contract.create_status(
        {
            "runtime": "ok",
            "internet_governance": "ok",
            "campaign_scheduler": "ok",
            "source_trust": "ok",
            "recovery": "ok",
            "dashboard": "ok",
        }
    )
    payload = status.as_dict()
    assert payload["status"] == "ready"
    assert contract.validate_status(payload) == []


def test_health_contract_blocks_missing_checks():
    contract = ProductionHealthContract()
    status = contract.create_status({"runtime": "ok"})
    payload = status.as_dict()
    assert payload["status"] == "blocked"
    assert payload["checks"]["dashboard"] == "missing"


def test_deployment_readiness_passes_with_required_capabilities(tmp_path: Path):
    validator = DeploymentReadinessValidator(project_root=tmp_path)
    report = validator.validate(
        capabilities={
            "governed_external_search",
            "persistent_campaigns",
            "campaign_scheduler",
            "runtime_recovery",
            "adaptive_source_trust",
            "source_quarantine",
            "operations_dashboard",
            "bounded_orchestration",
            "rollback_safety",
            "runtime_isolation",
        },
        env={"CLAIRE_ALLOWED_HOSTS": "localhost,127.0.0.1"},
        cors_origins=["https://example.com"],
        port=443,
        scan_secrets=True,
    )
    assert report.ready is True
    assert report.findings == []


def test_deployment_readiness_blocks_missing_capabilities(tmp_path: Path):
    validator = DeploymentReadinessValidator(project_root=tmp_path)
    report = validator.validate(
        capabilities={"governed_external_search"},
        env={},
        cors_origins=["https://example.com"],
        port=443,
        scan_secrets=False,
    )
    assert report.ready is False
    assert any(item.code == "missing_capability" for item in report.findings)


def test_manifest_shape_is_valid():
    manifest_path = Path("manifests/v17_48_deployment_production_hardening.json")
    if not manifest_path.exists():
        pytest.skip("manifest is installed by root installer")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    findings = RuntimeHardeningValidator().validate_manifest_shape(manifest)
    assert findings == []
