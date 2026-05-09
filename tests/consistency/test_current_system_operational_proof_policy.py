from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_OPERATIONAL_PROOF_FILES = [
    "claire/operational_proof/benchmark_replay_accumulator.py",
    "claire/operational_proof/outcome_label_adjudicator.py",
    "claire/operational_proof/operator_review_capture.py",
    "claire/operational_proof/drift_false_positive_tracker.py",
    "claire/operational_proof/confidence_calibration_reporter.py",
    "claire/operational_proof/pilot_readiness_gate.py",
    "claire/operational_proof/governance_deployment_lock.py",
    "claire/operational_proof/operational_proof_plateau.py",
]


def test_operational_proof_files_exist():
    missing = [
        rel
        for rel in REQUIRED_OPERATIONAL_PROOF_FILES
        if not (ROOT / rel).exists()
    ]

    assert not missing, (
        "Missing operational proof files: " + ", ".join(missing)
    )