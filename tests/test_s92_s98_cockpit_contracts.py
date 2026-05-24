from __future__ import annotations

from pathlib import Path

from runtime_core.api.governed_review_queue import enqueue_for_review
from runtime_core.api.governed_discovery_candidates import build_discovery_candidate
from runtime_core.api.governed_useful_outputs import build_useful_output_candidate
from runtime_core.api.governed_s92_s98_cockpit_contracts import (
    build_canonical_s85_s91_panel,
    build_review_queue_status,
    build_cockpit_evidence_output_card,
    perform_operator_review_action,
    build_route_demo_selector,
    build_end_to_end_cockpit_demo_proof,
)

def sample_evidence():
    return {
        "basket_id": "basket_s92_001",
        "trust_score": 0.83,
        "evidence_items": [
            {"evidence_id": "ev_s92_1", "title": "Portfolio market signal", "trust_score": 0.83},
            {"evidence_id": "ev_s92_2", "title": "Breakthrough design signal", "trust_score": 0.74},
        ],
    }

def sample_extraction():
    return {
        "extraction_id": "extract_s92_001",
        "signals": [
            {"label": "portfolio upside signal", "type": "portfolio", "confidence": 0.81},
            {"label": "design route implication", "type": "design", "confidence": 0.67},
        ],
    }

def test_s92_canonical_panel_reads_proof_payload(tmp_path: Path):
    panel = build_canonical_s85_s91_panel(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert panel["panel_version"] == "S92"
    assert panel["status"] == "ready"
    assert panel["read_only"] is True
    assert panel["locks"]["runtime_truth_write_blocked"] is True
    assert panel["export"]["status"] == "exported"

def test_s93_review_queue_status_is_read_only(tmp_path: Path):
    store = tmp_path / "review.json"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio"))
    enqueue_for_review(output, store_path=store, operator="pytest")
    status = build_review_queue_status(store_path=store)
    assert status["endpoint_contract_version"] == "S93"
    assert status["read_only"] is True
    assert status["total_items"] == 1
    assert status["counts"]["pending_review"] == 1

def test_s95_cockpit_card_uses_real_proof_payload(tmp_path: Path):
    card = build_cockpit_evidence_output_card(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert card["card_version"] == "S95"
    assert card["status"] == "ready"
    assert card["presentation_only"] is True
    assert card["export_status"] == "exported"

def test_s96_operator_action_contract_approves_and_exports(tmp_path: Path):
    store = tmp_path / "review.json"
    export_dir = tmp_path / "exports"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="portfolio"))
    item = enqueue_for_review(output, store_path=store, operator="pytest")
    result = perform_operator_review_action(item["review_item_id"], "approve", store_path=store, export_dir=export_dir, operator="pytest", note="approval for export proof")
    assert result["action_contract_version"] == "S96"
    assert result["decision"]["decision"] == "approved"
    assert result["export"]["status"] == "exported"
    assert result["locks"]["autonomous_execution_blocked"] is True

def test_s96_operator_action_contract_rejects_without_export(tmp_path: Path):
    store = tmp_path / "review.json"
    output = build_useful_output_candidate(build_discovery_candidate(sample_evidence(), sample_extraction(), requested_route="design"))
    item = enqueue_for_review(output, store_path=store, operator="pytest")
    result = perform_operator_review_action(item["review_item_id"], "reject", store_path=store, export_dir=tmp_path / "exports", operator="pytest")
    assert result["decision"]["decision"] == "rejected"
    assert result["export"] is None

def test_s97_route_demo_selector_supports_each_route(tmp_path: Path):
    for route in ("portfolio", "breakthrough", "design"):
        selected = build_route_demo_selector(route, sample_evidence(), sample_extraction(), store_path=tmp_path / f"{route}_review.json", export_dir=tmp_path / route / "exports", approve=False)
        assert selected["selector_contract_version"] == "S97"
        assert selected["selected_route"] == route
        assert selected["demo"]["status"] == "review_required"
        assert selected["locks"]["runtime_truth_mutation_blocked"] is True

def test_s98_end_to_end_cockpit_demo_proof(tmp_path: Path):
    proof = build_end_to_end_cockpit_demo_proof(sample_evidence(), sample_extraction(), store_path=tmp_path / "review.json", export_dir=tmp_path / "exports")
    assert proof["cockpit_demo_proof_version"] == "S98"
    assert proof["status"] == "ready"
    assert proof["canonical_panel"]["read_only"] is True
    assert proof["review_queue_status"]["total_items"] >= 1
    assert proof["export_manifest"]["export_count"] >= 1
    assert proof["cockpit_card"]["status"] == "ready"
