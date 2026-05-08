from claire.final_stability.final_freeze_checklist import FinalFreezeChecklist
from claire.final_stability.recovery_point_builder import RecoveryPointBuilder

def test_freeze_not_ready_when_empty():
    assert FinalFreezeChecklist().evaluate({})["status"] == "not_ready"

def test_recovery_point_version():
    assert RecoveryPointBuilder().build_recovery_point("11.90")["version"] == "11.90"
