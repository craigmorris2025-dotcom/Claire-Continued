from claire.recursive_platform_maturity.self_ingestion_contract import SelfIngestionContract
from claire.recursive_platform_maturity.maturity_cycle_tracker import MaturityCycleTracker

def test_self_ingestion_safe_mode():
    assert SelfIngestionContract().build_contract(["a"])["safe_mode"] is True

def test_cycle_recorded():
    assert MaturityCycleTracker().record_cycle("c1", "ok")["status"] == "recorded"
