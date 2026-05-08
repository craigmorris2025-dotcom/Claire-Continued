import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_orphan_dormant_module_detector_runs():
    result = subprocess.run([sys.executable, "tools/orphan_dormant_module_detector.py"], cwd=ROOT)
    assert result.returncode == 0
