from __future__ import annotations

import importlib


def test_s185_visual_controls_are_backend_owned_and_safe():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_visual_action_surface_contract()

    assert payload["stage"] == "S185"
    assert payload["backend_owned"] is True
    assert payload["cockpit_presentation_only"] is True
    assert payload["controls"]

    blocked = {c["action_id"]: c for c in payload["controls"] if not c["button_enabled"]}
    assert "execute_runtime_mutation" in blocked
    assert "enable_automatic_updates" in blocked
    assert "start_continuous_crawl" in blocked


def test_s186_monitoring_backend_core_preserves_locks():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_monitoring_backend_state()

    assert payload["stage"] == "S186"
    assert payload["health"]["backend"] == "available"
    assert payload["health"]["governance"] == "locked"
    assert payload["queues"]["web_jobs"]["continuous_allowed"] is False
    assert payload["queues"]["mutation_proposals"]["execution_allowed"] is False
    assert payload["locks"]["runtime_mutation_blocked"] is True
    assert payload["locks"]["automatic_updates_blocked"] is True
    assert payload["locks"]["autonomous_execution_blocked"] is True


def test_s187_operator_notifications_state_manual_promotion_and_locks():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_operator_notifications()

    ids = {n["notification_id"] for n in payload["notifications"]}
    assert "governance-locks-active" in ids
    assert "manual-promotion-required" in ids


def test_s188_panel_wiring_requires_consolidated_cockpit_surfaces():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_cockpit_panel_wiring_contract()

    panels = {p["panel_id"]: p for p in payload["panels"]}
    for required in [
        "command_bar",
        "runtime_status",
        "governance_locks",
        "web_jobs",
        "review_queue",
        "export_queue",
        "operator_notifications",
        "diagnostics_drawer",
    ]:
        assert required in panels
        assert panels[required]["required"] is True

    assert payload["frontend_authority"] == "presentation_only"


def test_s189_review_approval_blocks_unsafe_decisions():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_review_approval_contract()

    assert payload["stage"] == "S189"
    assert payload["manual_approval_mandatory"] is True
    assert payload["quarantine_mandatory"] is True

    blocked = set(payload["blocked_decisions"])
    assert "write_runtime_truth_directly" in blocked
    assert "execute_runtime_mutation" in blocked
    assert "enable_automatic_updates" in blocked
    assert "start_continuous_crawl" in blocked
    assert "autonomous_execute" in blocked


def test_s190_operational_cockpit_plateau_reached_without_unsafe_authority():
    module = importlib.import_module("claire.api.cockpit_visual_controls")
    payload = module.get_operational_cockpit_plateau()

    assert payload["stage"] == "S190"
    assert payload["plateau_reached"] is True
    assert payload["safe_forward_motion"] is True
    assert payload["contracts"]["monitoring"]["action_summary"]["unsafe_enabled"] == []
    assert "to_modern_enterprise_cockpit_dashboard_completion" in payload["countdown"]
