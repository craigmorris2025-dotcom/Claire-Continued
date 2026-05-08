from pathlib import Path


REQUIRED_OPERATIONAL_PROOF_FILES = [
    "src/claire/operational_proof/benchmark_replay_accumulator.py",
    "src/claire/operational_proof/outcome_label_adjudicator.py",
    "src/claire/operational_proof/operator_review_capture.py",
    "src/claire/operational_proof/drift_false_positive_tracker.py",
    "src/claire/operational_proof/confidence_calibration_reporter.py",
    "src/claire/operational_proof/pilot_readiness_gate.py",
    "src/claire/operational_proof/governance_deployment_lock.py",
    "src/claire/operational_proof/operational_proof_plateau.py",
]


def test_operational_proof_files_exist():
    root = Path(__file__).resolve().parents[2]
    missing = [rel for rel in REQUIRED_OPERATIONAL_PROOF_FILES if not (root / rel).exists()]
    assert not missing, "Missing operational proof files: " + ", ".join(missing)
