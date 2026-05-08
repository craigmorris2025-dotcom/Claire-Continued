from claire.operational_proof.operator_review_capture import OperatorReviewCapture

def test_capture_review():
    review = OperatorReviewCapture().capture_review("run1", "accepted", rationale="useful")
    assert review["decision"] == "accepted"
    assert review["record_type"] == "operator_review"
