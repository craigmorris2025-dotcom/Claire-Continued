from claire.external_review_readiness.redaction_checklist import RedactionChecklist
from claire.external_review_readiness.reviewer_packet_builder import ReviewerPacketBuilder

def test_redaction_blocks_empty():
    assert RedactionChecklist().evaluate({})["status"] == "blocked"

def test_packet_count():
    assert ReviewerPacketBuilder().build_packet("technical", ["readme"])["artifact_count"] == 1
