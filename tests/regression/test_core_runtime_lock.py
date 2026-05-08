import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_core_runtime_lock_passes():
    assert subprocess.run([sys.executable, "tools/core_runtime_lock.py"], cwd=ROOT).returncode == 0

def test_lifecycle_enforcement_check_passes():
    assert subprocess.run([sys.executable, "tools/lifecycle_enforcement_check.py"], cwd=ROOT).returncode == 0

def test_rollback_validation_runs():
    assert subprocess.run([sys.executable, "tools/rollback_validation.py"], cwd=ROOT).returncode == 0
