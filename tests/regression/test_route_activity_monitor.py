import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_route_activity_monitor_runs():
    result = subprocess.run([sys.executable, "tools/route_activity_monitor.py"], cwd=ROOT)
    assert result.returncode == 0
