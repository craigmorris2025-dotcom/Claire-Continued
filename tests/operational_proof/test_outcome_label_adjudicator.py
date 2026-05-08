from claire.operational_proof.outcome_label_adjudicator import OutcomeLabelAdjudicator

def test_adjudicate_label():
    label = OutcomeLabelAdjudicator().adjudicate("x1", "correct")
    assert label["status"] == "adjudicated"
    assert label["label"] == "correct"
