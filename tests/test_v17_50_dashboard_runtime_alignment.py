from pathlib import Path
import json


def test_button_registry_is_governed():
    from claire.dashboard.button_registry import get_button_registry, validate_button_registry

    buttons = get_button_registry()
    validation = validate_button_registry()
    assert validation["status"] == "ok"
    assert validation["button_count"] >= 6
    assert all(button["route"].startswith("/") for button in buttons)
    assert all(button["method"] in {"GET", "POST"} for button in buttons)
    assert all("governance_scope" in button for button in buttons)


def test_runtime_alignment_manifest_generation(tmp_path, monkeypatch):
    from claire.dashboard.runtime_alignment import build_capability_manifest, write_capability_manifest

    root = tmp_path
    (root / "src" / "frontend").mkdir(parents=True)
    (root / "src" / "frontend" / "index.html").write_text("<html><body></body></html>", encoding="utf-8")
    (root / "src" / "claire" / "api").mkdir(parents=True)
    (root / "src" / "claire" / "api" / "routes.py").write_text("from fastapi import APIRouter\nrouter = APIRouter()\n", encoding="utf-8")

    manifest = build_capability_manifest(root)
    assert manifest["version"] == "17.50"
    assert manifest["status"] == "aligned"
    assert "dashboard_action_buttons" in manifest["capabilities"]
    assert manifest["dashboard_buttons"]

    written = write_capability_manifest(root)
    out = root / "data" / "dashboard" / "dashboard_capability_manifest.json"
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8"))["version"] == "17.50"
    assert written["status"] == "aligned"


def test_dashboard_alignment_routes_importable():
    from claire.api.routes_dashboard_alignment import router

    paths = {route.path for route in router.routes}
    assert "/dashboard/alignment/status" in paths
    assert "/dashboard/alignment/capabilities" in paths
    assert "/dashboard/alignment/buttons" in paths
    assert "/dashboard/alignment/verify" in paths


def test_installed_manifest_exists_and_records_files():
    manifest_path = Path("manifests/v17_50_dashboard_runtime_alignment_manifest.json")
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == "17.50"
    assert manifest["build"] == "Dashboard Runtime Alignment + Action Buttons"
    assert "src/claire/dashboard/button_registry.py" in manifest["installed_files"]
    assert "src/frontend/claire_dashboard_actions.js" in manifest["installed_files"]
