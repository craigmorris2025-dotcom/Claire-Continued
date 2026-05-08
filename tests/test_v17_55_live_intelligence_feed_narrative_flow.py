from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "src" / "frontend" / "command_center" / "modern"

def test_v17_55_files_exist():
    assert (DASH / "index.html").exists()
    assert (DASH / "intelligence_feed.js").exists()
    assert (DASH / "product_dashboard.js").exists()
    assert (DASH / "product_dashboard.css").exists()
    assert (ROOT / "manifests" / "v17_55_live_intelligence_feed_narrative_flow.json").exists()

def test_v17_55_index_loads_feed_between_workspace_and_dashboard():
    html = (DASH / "index.html").read_text(encoding="utf-8")
    assert "Intelligence Feed" in html
    assert "intelligence_feed.js" in html
    assert html.index("workspace_persistence.js") < html.index("intelligence_feed.js") < html.index("product_dashboard.js")

def test_v17_55_feed_persistence_contract():
    js = (DASH / "intelligence_feed.js").read_text(encoding="utf-8")
    assert "claire_intelligence_feed_v17_55" in js
    assert "addInsight" in js
    assert "addNote" in js
    assert "seedDemoIfEmpty" in js
    assert "narratives" in js
    assert "whyItMatters" in js

def test_v17_55_dashboard_has_narrative_flow_features():
    js = (DASH / "product_dashboard.js").read_text(encoding="utf-8")
    assert "Live intelligence feed" in js
    assert "What changed?" in js
    assert "Why it matters" in js
    assert "Signal → evidence → thesis flow" in js
    assert "Add to intelligence feed" in js
    assert "Narrative timeline" in js
    assert "Insight cards" in js

def test_v17_55_styles_support_feed_visualization():
    css = (DASH / "product_dashboard.css").read_text(encoding="utf-8")
    assert "flow-lane" in css
    assert "flow-step" in css
    assert "insight-card" in css
    assert "mini-row" in css
