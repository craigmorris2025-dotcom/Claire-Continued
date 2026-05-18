from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s16_renderer_file_exists_and_is_presentation_only():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "governed_runtime_timeline.js"
    assert js_path.exists()
    text = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S16" in text
    assert "presentation_only_runtime_authority_blocked" in text
    assert "/dashboard/payload" in text
    assert "fetch(" in text
    assert "POST" not in text
    assert "PUT" not in text
    assert "DELETE" not in text


def test_s16_css_classification_markers_exist():
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "governed_runtime_timeline_s16.css"
    assert css_path.exists()
    text = css_path.read_text(encoding="utf-8")
    assert "timeline-severity-warning" in text
    assert "timeline-severity-recovered" in text
    assert "timeline-severity-guarded" in text


def test_s16_html_links_renderer_assets_when_shell_exists():
    candidates = [
        ROOT / "frontend" / "cockpit" / "shell" / "cockpit_shell.html",
        ROOT / "frontend" / "cockpit" / "index.html",
        ROOT / "frontend" / "command_center" / "modern" / "index.html",
    ]
    existing = [path for path in candidates if path.exists()]
    assert existing
    html = existing[0].read_text(encoding="utf-8")
    assert "governed_runtime_timeline.js" in html
    assert "governed_runtime_timeline_s16.css" in html
