from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "frontend" / "cockpit" / "modern" / "claire_cockpit_shell.js"


def test_s247_s253_shell_js_contains_render_rules_and_safe_endpoint_probes():
    js = JS.read_text(encoding="utf-8")

    assert "RENDER_RULES" in js
    assert "renderPayload" in js
    assert 'payload_status: "/dashboard/payload/status"' in js
    assert 'provider_status: "/api/dashboard/search/provider/status"' in js
    assert 'method: "GET"' in js
    assert "frontend_may_mutate_payload" not in js


def test_s247_s253_shell_js_keeps_blocked_actions_disabled():
    js = JS.read_text(encoding="utf-8")

    assert 'run_autonomous_update: "automatic_updates_blocked"' in js
    assert 'execute_runtime_mutation: "runtime_mutation_blocked"' in js
    assert 'start_continuous_crawl: "continuous_crawling_blocked"' in js
    assert 'promote_without_review: "manual_promotion_mandatory"' in js
    assert "node.disabled = true" in js
