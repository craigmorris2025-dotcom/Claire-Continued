from __future__ import annotations

from claire.api.cockpit_disabled_button_behavior import get_disabled_button_behavior_contract
from claire.api.cockpit_endpoint_health_visibility import get_endpoint_health_visibility_contract


def test_s233_s239_disabled_button_behavior_keeps_unsafe_actions_disabled_with_safe_redirects():
    payload = get_disabled_button_behavior_contract()
    buttons = {button["button_id"]: button for button in payload["buttons"]}

    assert payload["disabled_buttons_must_explain_reason"] is True
    assert payload["frontend_may_enable_blocked_buttons"] is False

    assert buttons["run_autonomous_update"]["enabled"] is False
    assert buttons["run_autonomous_update"]["safe_redirect"] == "create_update_proposal"
    assert buttons["execute_runtime_mutation"]["reason"] == "runtime_mutation_blocked"
    assert buttons["start_continuous_crawl"]["safe_redirect"] == "request_bounded_web_job"
    assert buttons["promote_without_review"]["reason"] == "manual_promotion_mandatory"


def test_s233_s239_endpoint_health_visibility_separates_critical_from_diagnostics():
    payload = get_endpoint_health_visibility_contract()
    checks = {check["endpoint_id"]: check for check in payload["checks"]}

    assert payload["show_critical_failures_in_main_cockpit"] is True
    assert payload["hide_noncritical_details_in_diagnostics"] is True

    assert checks["canonical_payload"]["critical"] is True
    assert checks["canonical_payload"]["display_region"] == "monitoring_column"
    assert checks["docs"]["critical"] is False
    assert checks["docs"]["display_region"] == "diagnostics_drawer"
