from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "src" / "frontend" / "command_center" / "modern"


def test_v17_52_dashboard_files_exist():
    assert (DASH / "index.html").exists()
    assert (DASH / "operator_dashboard.css").exists()
    assert (DASH / "operator_dashboard.js").exists()
    assert (ROOT / "manifests" / "v17_52_modern_operator_dashboard.json").exists()


def test_v17_52_index_is_operator_dashboard_not_build_layer():
    html = (DASH / "index.html").read_text(encoding="utf-8")
    assert "Claire Syntalion Operator Dashboard" in html
    assert "Modern Operator Dashboard" in html
    assert "Internet Ops" in html
    assert "Campaigns" in html
    assert "Source Trust" in html
    assert "Launch Lock" in html


def test_v17_52_dashboard_has_runtime_aware_routes_and_no_fake_success_rule():
    js = (DASH / "operator_dashboard.js").read_text(encoding="utf-8")
    assert "/health" in js
    assert "/internet/ops/dashboard" in js
    assert "/internet/campaigns" in js
    assert "/internet/source-trust" in js
    assert "/launch/regression-lock" in js
    assert "Needs wiring" in js
    assert "Missing" in js
    assert "Not yet proven" in js


def test_v17_52_dashboard_has_modern_responsive_layout():
    css = (DASH / "operator_dashboard.css").read_text(encoding="utf-8")
    assert "app-shell" in css
    assert "content-grid" in css
    assert "status-strip" in css
    assert "@media" in css
    assert "backdrop-filter" in css


def test_v17_52_internet_dashboard_redirects_to_main_operator_dashboard():
    html = (DASH / "internet_operations_dashboard.html").read_text(encoding="utf-8")
    assert "url=./index.html" in html
    assert "moved into the main Claire Operator Dashboard" in html
