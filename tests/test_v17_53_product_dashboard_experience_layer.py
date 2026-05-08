from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "src" / "frontend" / "command_center" / "modern"

def test_v17_53_product_dashboard_files_exist():
    assert (DASH / "index.html").exists()
    assert (DASH / "product_dashboard.css").exists()
    assert (DASH / "product_dashboard.js").exists()
    assert (ROOT / "manifests" / "v17_53_product_dashboard_experience_layer.json").exists()

def test_v17_53_dashboard_is_user_active_not_dev_only():
    html = (DASH / "index.html").read_text(encoding="utf-8")
    assert "Your strategic intelligence workspace" in html
    assert "Start Discovery" in html
    assert "Discover" in html
    assert "Campaigns" in html
    assert "Evidence" in html
    assert "Portfolio" in html
    assert "Launch Center" in html

def test_v17_53_has_guided_workflows_and_empty_states():
    js = (DASH / "product_dashboard.js").read_text(encoding="utf-8")
    assert "Create a discovery brief" in js
    assert "Campaign workspace" in js
    assert "Evidence inbox" in js
    assert "Trust center" in js
    assert "Portfolio intelligence" in js
    assert "No active campaign displayed yet" in js
    assert "No portfolio view generated yet" in js

def test_v17_53_preserves_governed_route_awareness():
    js = (DASH / "product_dashboard.js").read_text(encoding="utf-8")
    assert "/health" in js
    assert "/internet/ops/dashboard" in js
    assert "/internet/campaigns" in js
    assert "/internet/source-trust" in js
    assert "/launch/regression-lock" in js
    assert "Fake success allowed" in js
    assert "Never" in js

def test_v17_53_has_modern_product_styles():
    css = (DASH / "product_dashboard.css").read_text(encoding="utf-8")
    assert "brand-orb" in css
    assert "workflow" in css
    assert "empty" in css
    assert "backdrop-filter" in css
    assert "@media" in css
