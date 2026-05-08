from claire.operational_proof.confidence_calibration_reporter import ConfidenceCalibrationReporter

def test_calibration_report():
    report = ConfidenceCalibrationReporter().build_report([{"confidence": 1.0, "outcome": "success"}])
    assert report["calibration_level"] == "strong"
