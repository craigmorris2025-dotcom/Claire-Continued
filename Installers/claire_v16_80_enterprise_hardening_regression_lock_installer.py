from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("tests/enterprise/test_v16_80_enterprise_hardening_regression.py", r"""
from pathlib import Path

from claire.enterprise.dependency_governance_snapshot import build_dependency_governance_snapshot
from claire.enterprise.runtime_health_recovery_diagnostics import build_runtime_health_recovery_diagnostics
from claire.enterprise.install_environment_verification import verify_install_environment
from claire.enterprise.enterprise_deployment_manifest import build_enterprise_deployment_manifest


def test_dependency_governance_snapshot_builds():
    snapshot = build_dependency_governance_snapshot()
    assert snapshot["status"] == "ready"
    assert Path("data/enterprise/dependency_governance_snapshot.json").exists()


def test_runtime_health_recovery_diagnostics_builds():
    report = build_runtime_health_recovery_diagnostics()
    assert "checked_count" in report
    assert Path("data/enterprise/runtime_health_recovery_diagnostics.json").exists()


def test_install_environment_verification_builds():
    report = verify_install_environment()
    assert "module_checks" in report
    assert Path("data/enterprise/install_environment_verification.json").exists()


def test_enterprise_deployment_manifest_builds():
    manifest = build_enterprise_deployment_manifest()
    assert manifest["status"] == "scaffold_ready"
    assert "deployment_profiles" in manifest
    assert Path("data/enterprise/enterprise_deployment_manifest.json").exists()
""")

print("v16.80 enterprise hardening regression lock installed.")
print("Run: pytest tests/enterprise/test_v16_80_enterprise_hardening_regression.py")
