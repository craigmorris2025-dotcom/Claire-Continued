from claire.valuation_demo_binder.valuation_memo_builder import ValuationMemoBuilder
from claire.valuation_demo_binder.demo_evidence_binder import DemoEvidenceBinder

def test_valuation_memo():
    assert ValuationMemoBuilder().build_memo("$2M-$8M", ["demo"])["record_type"] == "valuation_memo"

def test_demo_binder_count():
    assert DemoEvidenceBinder().build_binder(["a", "b"])["artifact_count"] == 2
