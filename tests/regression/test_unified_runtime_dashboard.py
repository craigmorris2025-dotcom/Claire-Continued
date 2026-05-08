import subprocess, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_unified_runtime_dashboard_builder_runs():
    result = subprocess.run([sys.executable, "tools/unified_runtime_dashboard_builder.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    data = json.loads((ROOT / "data" / "runtime" / "unified_runtime_dashboard.json").read_text(encoding="utf-8"))
    assert data["dashboard"] == "unified_runtime_dashboard"

def test_unified_runtime_dashboard_imports():
    from claire.dashboard.unified_runtime_dashboard import build_unified_runtime_dashboard
    payload = build_unified_runtime_dashboard(ROOT)
    assert payload["status"] == "available"
