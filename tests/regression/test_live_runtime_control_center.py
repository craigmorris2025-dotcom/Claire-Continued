import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_live_runtime_control_center_runs():
    result = subprocess.run([sys.executable, "tools/live_runtime_control_center.py"], cwd=ROOT)
    assert result.returncode == 0

def test_runtime_control_center_imports():
    from claire.dashboard.runtime_control_center import load_runtime_control_center
    payload = load_runtime_control_center(ROOT)
    assert "operator_status" in payload or "status" in payload
