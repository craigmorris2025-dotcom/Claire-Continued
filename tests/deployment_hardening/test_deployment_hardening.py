from claire.deployment_hardening.release_gate_evaluator import ReleaseGateEvaluator
from claire.deployment_hardening.preflight_checklist import PreflightChecklist

def test_release_gate_blocks_missing():
    assert ReleaseGateEvaluator().evaluate({})["status"] == "blocked"

def test_preflight_passes_all_true():
    assert PreflightChecklist().build({"launcher": True, "dashboard": True, "pytest": True, "version_lock": True, "rollback": True, "audit_report": True})["status"] == "pass"
