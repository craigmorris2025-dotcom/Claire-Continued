
from pathlib import Path

from claire.demo.demo_scenario_registry import load_demo_scenarios, seed_demo_scenarios
from claire.demo.guided_demo_runner import run_guided_demo
from claire.proof.proof_record_store import add_proof_record, list_proof_records
from claire.proof.evidence_binder_generator import build_evidence_binder


def test_demo_scenarios_seed():
    payload = seed_demo_scenarios()
    assert payload["scenario_count"] >= 3
    assert Path("data/demo/demo_scenarios.json").exists()


def test_guided_demo_runner_outputs_demo_ready():
    result = run_guided_demo()
    assert result["status"] == "demo_ready"
    assert Path("data/demo/guided_demo_run.json").exists()


def test_proof_record_store_adds_record():
    record = add_proof_record(
        "demo_run",
        "Regression demo proof record",
        {"status": "passed", "source": "v16.60 regression"},
    )
    assert record["record_type"] == "demo_run"
    assert len(list_proof_records()) >= 1


def test_evidence_binder_builds():
    binder = build_evidence_binder()
    assert binder["status"] == "ready"
    assert Path("data/proof/evidence_binder.json").exists()
