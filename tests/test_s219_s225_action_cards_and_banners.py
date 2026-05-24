from __future__ import annotations

from runtime_core.api.cockpit_action_card_ordering import get_action_card_ordering
from runtime_core.api.cockpit_warning_banner_contracts import get_warning_banner_contracts


def test_s219_s225_action_card_ordering_prioritizes_governance_and_next_action():
    payload = get_action_card_ordering()
    cards = {card["card_id"]: card for card in payload["cards"]}

    assert cards["governance_locks"]["priority"] == 1
    assert cards["next_action"]["priority"] < cards["bounded_jobs"]["priority"]
    assert cards["blocked_capabilities"]["always_visible"] is False


def test_s219_s225_warning_banners_redirect_unsafe_actions():
    payload = get_warning_banner_contracts()
    banners = {banner["banner_id"]: banner for banner in payload["banners"]}

    assert payload["unsafe_actions_redirected"] is True
    assert banners["runtime_mutation_blocked"]["operator_action"] == "review_proposal_only"
    assert banners["automatic_updates_blocked"]["operator_action"] == "create_update_proposal"
    assert banners["continuous_crawling_blocked"]["operator_action"] == "request_bounded_job"
    assert banners["manual_promotion_required"]["severity"] == "warning"
