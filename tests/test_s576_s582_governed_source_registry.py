from __future__ import annotations

from pathlib import Path


def test_s576_s582_source_registry_payload_preserves_all_blocks():
    from runtime_core.governance.governed_source_registry import get_source_registry_payload

    payload = get_source_registry_payload()
    assert payload["version"] == "v19.89.8-S576-S582"
    assert payload["readiness"] == "source_registry_ready_governed_blocked"
    assert payload["summary"]["total_sources"] >= 8
    assert payload["summary"]["allowlisted_metadata_only"] >= 5
    assert payload["summary"]["quarantined"] >= 1
    assert payload["stop_gate"]["build"] == "S582"

    blocked = payload["blocked_capabilities"]
    assert blocked["live_web_execution_enabled"] is False
    assert blocked["browser_execution_enabled"] is False
    assert blocked["network_request_performed"] is False
    assert blocked["body_read_allowed"] is False
    assert blocked["autonomous_crawling_enabled"] is False
    assert blocked["automatic_updates_enabled"] is False
    assert blocked["runtime_mutation_enabled"] is False
    assert blocked["package_download_performed"] is False
    assert blocked["package_install_performed"] is False
    assert blocked["command_execution_enabled"] is False


def test_s576_s582_trust_tiers_allowlist_quarantine_and_cards():
    from runtime_core.governance.governed_source_registry import (
        TRUST_TIERS,
        build_governed_source_registry_payload,
        classify_source,
    )

    assert "tier_1_authoritative" in TRUST_TIERS
    assert "tier_4_unknown" in TRUST_TIERS

    official = classify_source({"label": "SEC", "domain": "https://www.sec.gov/filings", "source_type": "regulatory"}).to_dict()
    assert official["domain"] == "sec.gov"
    assert official["allowlisted"] is True
    assert official["status"] == "allowlisted_metadata_only"
    assert official["body_read_allowed"] is False
    assert "body-read" in official["blocked_uses"]

    unknown = classify_source({"label": "Unknown", "domain": "unknown.example", "source_type": "unknown"}).to_dict()
    assert unknown["quarantined"] is True
    assert unknown["status"] == "quarantine_by_default"

    payload = build_governed_source_registry_payload()
    assert payload["source_cards"]
    assert all(card["policy"]["body_read_allowed"] is False for card in payload["source_cards"])
    assert any("quarantined" in card["badges"] for card in payload["source_cards"])


def test_s576_s582_governed_actions_are_registered_but_execution_blocked():
    from runtime_core.governance.governed_source_registry import get_source_actions_payload

    payload = get_source_actions_payload()
    actions = payload["governed_actions"]
    assert len(actions) >= 3
    assert {action["action_id"] for action in actions} >= {
        "source_registry.review_candidates",
        "source_registry.inspect_quarantine",
        "source_registry.export_policy_snapshot",
    }
    assert all(action["enabled"] is False for action in actions)
    assert all(action["execution_blocked"] is True for action in actions)


def test_s576_s582_api_route_functions_return_cockpit_payloads():
    from runtime_core.api.governed_source_registry_routes import (
        read_source_actions,
        read_source_cards,
        read_source_policy,
        read_source_registry,
        read_source_status,
    )

    registry = read_source_registry()
    cards = read_source_cards()
    actions = read_source_actions()
    policy = read_source_policy()
    status = read_source_status()

    assert registry["cockpit_panels"]["governed_web"]["cards"]
    assert cards["source_cards"]
    assert actions["governed_actions"]
    assert policy["trust_tiers"]
    assert status["stop_gate"]["next_phase"] == "S583-S589 Search Plan + Query Governance"


def test_s576_s582_cockpit_assets_exist_and_point_to_source_registry_endpoint():
    js_path = Path("frontend/cockpit/assets/claire_governed_source_registry.js")
    css_path = Path("frontend/cockpit/assets/claire_governed_source_registry.css")
    assert js_path.exists()
    assert css_path.exists()
    js = js_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    assert "/api/sources/registry" in js
    assert "/api/sources/actions" in js
    assert "Governed Source Registry" in js
    assert ".claire-source-registry-panel" in css

