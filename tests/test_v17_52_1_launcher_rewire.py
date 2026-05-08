from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v17_52_1_launcher_points_to_operator_dashboard():
    launcher = ROOT / "LAUNCH_CLAIRE.bat"
    assert launcher.exists()
    text = launcher.read_text(encoding="utf-8")
    assert "Version: 17.52.1" in text
    assert "modern_operator_dashboard" in text
    assert "src\\frontend\\command_center\\modern\\index.html" in text or "src\frontend\command_center\modern\index.html" in text
    assert "Opening modern Claire Operator Dashboard" in text


def test_v17_52_1_operator_dashboard_exists():
    dashboard = ROOT / "src" / "frontend" / "command_center" / "modern" / "index.html"
    assert dashboard.exists()
    text = dashboard.read_text(encoding="utf-8")
    assert "Claire Syntalion Operator Dashboard" in text
    assert "Modern Operator Dashboard" in text
