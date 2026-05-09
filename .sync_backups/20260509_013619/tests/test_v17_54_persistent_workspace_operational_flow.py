from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "src" / "frontend" / "command_center" / "modern"

def test_v17_54_files_exist():
    assert (DASH / "index.html").exists()
    assert (DASH / "workspace_persistence.js").exists()
    assert (DASH / "product_dashboard.js").exists()
    assert (ROOT / "manifests" / "v17_54_persistent_workspace_operational_flow.json").exists()

def test_v17_54_dashboard_loads_persistence_before_product_dashboard():
    html = (DASH / "index.html").read_text(encoding="utf-8")
    assert "workspace_persistence.js" in html
    assert "product_dashboard.js" in html
    assert html.index("workspace_persistence.js") < html.index("product_dashboard.js")
    assert 'data-page="workspace"' in html

def test_v17_54_workspace_persistence_has_local_storage_contract():
    js = (DASH / "workspace_persistence.js").read_text(encoding="utf-8")
    assert "localStorage" in js
    assert "claire_workspace_v17_54" in js
    assert "saveDiscovery" in js
    assert "saveCampaignDraft" in js
    assert "addActivity" in js
    assert "clearWorkspace" in js

def test_v17_54_product_dashboard_has_workspace_flow():
    js = (DASH / "product_dashboard.js").read_text(encoding="utf-8")
    assert "Workspace memory" in js
    assert "Continue where you left off" in js
    assert "Save discovery draft" in js
    assert "Save campaign draft" in js
    assert "Recent activity" in js
    assert "Workspace continuity" in js
