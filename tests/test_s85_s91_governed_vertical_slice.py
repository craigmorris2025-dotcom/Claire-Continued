from __future__ import annotations

import json
from pathlib import Path

from runtime_core.api.governed_discovery_candidates import build_discovery_candidate, build_route_discovery_candidates
from runtime_core.api.governed_useful_outputs import build_useful_output_candidate
from runtime_core.api.governed_review_queue import decide_review_item, enqueue_for_review, list_review_queue
from runtime_core.api.governed_reviewed_exports import export_reviewed_output
from runtime_core.api.governed_route_repeat import build_route_repeat_payload
from runtime_core.api.governed_demo_run import build_demo_contract, build_demo_readiness_proof
from runtime_core.api.governed_s85_s91_payload import build_s85_s91_payload

def sample_evidence():
    return {
        "basket_id": "basket_test_001",
        "trust_score": 0.8,
        "evidence_items": [
            {"evidence_id": "ev1", "title": "Portfolio market signal", "trust_score": 0.8},
            {"evidence_id": "ev2", "title": "Design architecture implication", "trust_score": 0.7},
        ],
    }

def sample_extraction():
    return {
        "extraction_id": "extract_test_001",
        "signals": [
            {"label": "portfolio risk signal", "type": "portfolio", "confidence": 0.9},
            {"label": "component design signal", "type": "design", "confidence": 0.7},
        ],
        "entities": [{"name": "Example Company", "type": "organization"}],
    }

def test_s85_discovery_candidate_from_evidence_is_quarantined():
    candidate = build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio")
    assert candidate["candidate_version"] == "S85"
    assert candidate["status"] == "quarantined_candidate"
    assert candidate["candidate_type"] == "portfolio"
    assert candidate["authority"]["runtime_truth_write"] == "blocked"
    assert candidate["authority"]["manual_review_required"] is True
    assert candidate["source_evidence_ids"] == ["ev1", "ev2"]

def test_s86_useful_output_candidate_requires_review():
    discovery = build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="design")
    output = build_useful_output_candidate(discovery)
    assert output["candidate_version"] == "S86"
    assert output["route"] == "design"
    assert output["status"] == "review_required"
    assert output["authority"]["runtime_truth_write"] == "blocked"
    assert output["authority"]["export_allowed_after_approval"] is True

def test_s87_review_queue_approval_flow(tmp_path: Path):
    store = tmp_path / "review.json"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio"))
    item = enqueue_for_review(output, store_path=store, operator="pytest")
    decision = decide_review_item(item["review_item_id"], "approved", store_path=store, operator="pytest")
    queue = list_review_queue(store_path=store)
    assert item["status"] == "pending_review"
    assert decision["review_item"]["status"] == "approved"
    assert decision["decision"]["runtime_truth_write"] == "blocked"
    assert len(queue["queue"]) == 1
    assert len(queue["decisions"]) == 1

def test_s88_export_reviewed_output_only_after_approval(tmp_path: Path):
    store = tmp_path / "review.json"
    export_dir = tmp_path / "exports"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio"))
    item = enqueue_for_review(output, store_path=store, operator="pytest")
    decision = decide_review_item(item["review_item_id"], "approved", store_path=store, operator="pytest")
    exported = export_reviewed_output(decision["review_item"], export_dir=export_dir)
    path = Path(exported["path"])
    assert exported["status"] == "exported"
    assert exported["runtime_truth_write"] == "blocked"
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["audit"]["export_is_derived_artifact"] is True

def test_s88_export_blocks_unapproved_items(tmp_path: Path):
    store = tmp_path / "review.json"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio"))
    item = enqueue_for_review(output, store_path=store, operator="pytest")
    try:
        export_reviewed_output(item, export_dir=tmp_path / "exports")
    except PermissionError:
        pass
    else:
        raise AssertionError("unapproved export should be blocked")

def test_s89_route_repeat_for_portfolio_breakthrough_design(tmp_path: Path):
    payload = build_route_repeat_payload(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json")
    assert payload["route_repeat_version"] == "S89"
    assert payload["status"] == "route_repeat_ready"
    assert set(payload["routes"]) == {"portfolio", "breakthrough", "design"}
    assert set(payload["discovery_candidates"]) == {"portfolio", "breakthrough", "design"}
    assert set(payload["useful_output_candidates"]) == {"portfolio", "breakthrough", "design"}
    assert set(payload["review_items"]) == {"portfolio", "breakthrough", "design"}

def test_s90_demo_contract_runs_evidence_to_export(tmp_path: Path):
    demo = build_demo_contract(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports", approve=True)
    assert demo["demo_contract_version"] == "S90"
    assert demo["status"] == "demo_export_ready"
    assert demo["review_decision"]["decision"] == "approved"
    assert demo["export"]["status"] == "exported"
    assert demo["authority"]["runtime_truth_write"] == "blocked"

def test_s91_demo_readiness_proof_has_full_chain(tmp_path: Path):
    proof = build_demo_readiness_proof(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    chain = proof["proof_chain"]
    assert proof["demo_readiness_version"] == "S91"
    assert proof["status"] == "ready"
    assert all(chain.values())

def test_s85_s91_payload_is_cockpit_readable_without_runtime_mutation(tmp_path: Path):
    payload = build_s85_s91_payload(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert payload["version"] == "v19.89.8-S85-S91"
    assert payload["status"] == "ready"
    assert payload["proof"]["demo"]["authority"]["runtime_truth_mutation"] == "blocked"
    assert payload["proof"]["demo"]["export"]["derived_artifact"] is True

def test_route_candidates_are_deterministic_per_route_shape():
    candidates = build_route_discovery_candidates(sample_evidence(), sample_extraction())
    assert set(candidates.keys()) == {"portfolio", "breakthrough", "design"}
    for route, candidate in candidates.items():
        assert candidate["candidate_type"] == route
        assert candidate["status"] == "quarantined_candidate"
        assert candidate["authority"]["promotion_allowed"] is False
