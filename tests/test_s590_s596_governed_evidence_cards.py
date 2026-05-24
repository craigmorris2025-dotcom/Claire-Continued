from __future__ import annotations

from pathlib import Path


def test_s590_s596_evidence_payload_preserves_all_blocks():
    from runtime_core.governance.governed_evidence_cards import get_governed_evidence_payload

    payload = get_governed_evidence_payload()
    assert payload["version"] == "v19.89.8-S590-S596"
    assert payload["readiness"] == "governed_evidence_cards_ready_execution_blocked"
    assert payload["summary"]["total_evidence_cards"] >= 1
    assert payload["stop_gate"]["build"] == "S596"

    blocked = payload["blocked_capabilities"]
    assert blocked["live_web_execution_enabled"] is False
    assert blocked["browser_execution_enabled"] is False
    assert blocked["search_provider_execution_enabled"] is False
    assert blocked["network_request_performed"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["autonomous_crawling_enabled"] is False
    assert blocked["automatic_updates_enabled"] is False
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["package_download_performed"] is False
    assert blocked["package_install_performed"] is False
    assert blocked["command_execution_enabled"] is False


def test_s590_s596_evidence_cards_are_normalized_for_cockpit_review():
    from runtime_core.governance.governed_evidence_cards import build_evidence_cards

    cards = build_evidence_cards()
    assert cards
    for card in cards:
        assert card["id"]
        assert card["title"]
        assert card["card_type"] in {
            "source_registry_evidence",
            "search_plan_evidence",
            "evidence_stub",
        }
        assert card["policy"]["cockpit_render_allowed"] is True
        assert card["policy"]["operator_review_allowed"] is True
        assert card["policy"]["provider_probe_allowed"] is False
        assert card["policy"]["network_request_allowed"] is False
        assert card["policy"]["body_read_allowed"] is False
        assert card["policy"]["runtime_mutation_allowed"] is False
        assert card["provenance"]["network_request_performed"] is False
        assert card["provenance"]["body_read_performed"] is False
        assert card["provenance"]["runtime_truth_mutated"] is False


def test_s590_s596_review_queue_and_actions_are_visible_but_not_executable():
    from runtime_core.governance.governed_evidence_cards import (
        build_evidence_cards,
        build_governed_actions,
        build_review_queue,
    )

    cards = build_evidence_cards()
    queue = build_review_queue(cards)
    actions = build_governed_actions(cards)

    assert len(queue) == len(cards)
    assert actions
    assert all(item["operator_visible"] is True for item in queue)
    assert all(item["execution_allowed"] is False for item in queue)
    assert all(item["promotion_allowed"] is False for item in queue)
    assert all(action["operator_visible"] is True for action in actions)
    assert all(action["enabled"] is False for action in actions)
    assert all(action["execution_blocked"] is True for action in actions)
    assert any(action["id"] == "review_evidence_cards" for action in actions)


def test_s590_s596_api_route_functions_return_evidence_surfaces():
    from runtime_core.api.governed_evidence_card_routes import (
        read_governed_evidence_actions,
        read_governed_evidence_cards,
        read_governed_evidence_payload,
        read_governed_evidence_policy,
        read_governed_evidence_review,
        read_governed_evidence_status,
    )

    cards = read_governed_evidence_cards()
    review = read_governed_evidence_review()
    actions = read_governed_evidence_actions()
    policy = read_governed_evidence_policy()
    status = read_governed_evidence_status()
    payload = read_governed_evidence_payload()

    assert cards["evidence_cards"]
    assert review["review_queue"]
    assert actions["governed_actions"]
    assert policy["policy"]["network_request_allowed"] is False
    assert status["stop_gate"]["next_phase"] == "S597-S603 Source Review Queue + Metadata Probe Gate Planning"
    assert payload["cockpit_panels"]["evidence_review"]["cards"]


def test_s590_s596_cockpit_assets_exist_and_reference_evidence_endpoints():
    js_path = Path("frontend/cockpit/assets/claire_governed_evidence_cards.js")
    css_path = Path("frontend/cockpit/assets/claire_governed_evidence_cards.css")
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "/api/evidence/governed/status" in js
    assert "/api/evidence/governed/cards" in js
    assert "/api/evidence/governed/actions" in js
    assert "Evidence cards ready for review" in js
    assert ".claire-evidence-panel" in css

