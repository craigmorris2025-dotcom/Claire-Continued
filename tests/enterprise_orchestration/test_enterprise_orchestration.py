from claire.enterprise_orchestration.operator_role_registry import OperatorRoleRegistry
from claire.enterprise_orchestration.access_review_gate import AccessReviewGate

def test_roles_include_owner():
    assert "owner" in OperatorRoleRegistry().build_roles()["roles"]

def test_access_blocks_unreviewed():
    assert AccessReviewGate().evaluate(False, True)["status"] == "blocked"
