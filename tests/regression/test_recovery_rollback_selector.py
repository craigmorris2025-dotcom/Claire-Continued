import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_recovery_rollback_selector_runs():
    result = subprocess.run([sys.executable, "tools/recovery_rollback_selector.py"], cwd=ROOT)
    assert result.returncode == 0
