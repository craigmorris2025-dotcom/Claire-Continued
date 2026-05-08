import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_live_runtime_dashboard_state_builds():
    result = subprocess.run([sys.executable, "tools/live_runtime_dashboard_state.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    path = ROOT / "data" / "runtime" / "live_runtime_dashboard_state.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["dashboard"] == "live_runtime_dashboard_state"

def test_live_runtime_state_loader_imports():
    from claire.dashboard.live_runtime_state import load_live_runtime_state
    state = load_live_runtime_state(ROOT)
    assert "status" in state
