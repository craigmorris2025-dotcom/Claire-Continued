from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "frontend" / "cockpit" / "modern"


def test_s254_s260_shell_html_contains_governance_banner_stack():
    html = (SHELL / "claire_cockpit_shell.html").read_text(encoding="utf-8")

    assert 'id="governance_banner_stack"' in html
    assert 'data-card-id="governance_banner_backend_owns_truth"' in html
    assert 'data-card-id="governance_banner_manual_promotion"' in html
    assert 'data-card-id="governance_banner_quarantine"' in html
    assert 'data-card-id="governance_banner_updates_blocked"' in html
    assert 'data-card-id="governance_banner_mutation_blocked"' in html


def test_s254_s260_shell_js_contains_action_intents_and_safe_handlers():
    js = (SHELL / "claire_cockpit_shell.js").read_text(encoding="utf-8")

    assert "ACTION_INTENTS" in js
    assert "attachSafeActionIntentHandlers" in js
    assert "renderGovernanceBanners" in js
    assert 'request_bounded_web_job: "proposal_only"' in js
    assert 'execute_runtime_mutation: "blocked"' in js
    assert "Blocked action:" in js


def test_s254_s260_shell_css_places_governance_banners_without_replacing_existing_regions():
    css = (SHELL / "claire_cockpit_shell.css").read_text(encoding="utf-8")

    assert "#governance_banner_stack" in css
    assert '"banners monitor"' in css
    assert "#top_command_bar" in css
    assert "#primary_runtime_panel" in css
    assert "#operations_strip" in css
