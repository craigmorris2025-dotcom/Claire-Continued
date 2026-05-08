from claire.autonomous_research_ecosystem.source_policy_gate import SourcePolicyGate
from claire.autonomous_research_ecosystem.synthesis_review_queue import SynthesisReviewQueue

def test_source_policy_blocks_unknown():
    assert SourcePolicyGate().evaluate("x", [])["status"] == "blocked"

def test_review_queue():
    assert SynthesisReviewQueue().queue_item("i1", "summary")["status"] == "queued_for_review"
