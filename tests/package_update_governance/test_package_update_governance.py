from claire.package_update_governance.package_update_policy import PackageUpdatePolicy
from claire.package_update_governance.update_plan_builder import UpdatePlanBuilder

def test_policy_blocks_missing_steps():
    assert PackageUpdatePolicy().evaluate([])["status"] == "blocked"

def test_update_plan_requires_rollback():
    assert UpdatePlanBuilder().build_plan(["httpx"], "live connectivity")["rollback_required"] is True
