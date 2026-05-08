import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_install_governance_dashboard_runs():
    result = subprocess.run([sys.executable, "tools/install_governance_dashboard.py"], cwd=ROOT)
    assert result.returncode == 0
