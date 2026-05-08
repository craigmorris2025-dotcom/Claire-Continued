from claire.online_ops_endgame.provider_adapter_contract import ProviderAdapterContract
from claire.online_ops_endgame.industry_standard_readiness_check import IndustryStandardReadinessCheck

def test_provider_contract_controls():
    contract = ProviderAdapterContract().build_contract("web_search", ["search"])
    assert "audit_log" in contract["required_controls"]

def test_industry_standard_check_blocks_empty():
    assert IndustryStandardReadinessCheck().evaluate({})["status"] == "not_ready"
