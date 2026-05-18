from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_s31r2_dock_assets_exist():
    js_path = ROOT / "frontend" / "cockpit" / "assets" / "js" / "operational_expansion_dock_s31r2.js"
    css_path = ROOT / "frontend" / "cockpit" / "assets" / "css" / "operational_expansion_dock_s31r2.css"

    assert js_path.exists()
    assert css_path.exists()

    js = js_path.read_text(encoding="utf-8")
    assert "v19.89.8-S31R2" in js
    assert "/dashboard/payload" in js
    assert "presentation_only_runtime_authority_blocked" in js
    assert "POST" not in js
    assert "PUT" not in js
    assert "DELETE" not in js


def test_s31r2_dock_is_linked_to_some_shell():
    candidates = [
        ROOT / "frontend" / "cockpit" / "shell" / "cockpit_shell.html",
        ROOT / "frontend" / "cockpit" / "index.html",
        ROOT / "frontend" / "command_center" / "modern" / "index.html",
    ]
    shells = [path for path in candidates if path.exists()]
    assert shells

    assert any("operational_expansion_dock_s31r2.js" in path.read_text(encoding="utf-8") for path in shells)
