from claire.operational_proof.drift_false_positive_tracker import DriftFalsePositiveTracker

def test_drift_severity():
    rec = DriftFalsePositiveTracker().record_drift("run1", 0.8, 0.4)
    assert rec["severity"] == "high"
