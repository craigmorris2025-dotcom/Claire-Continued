import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_safe_archive_recommender_runs():
    subprocess.run([sys.executable, "tools/orphan_dormant_module_detector.py"], cwd=ROOT)
    result = subprocess.run([sys.executable, "tools/safe_archive_recommender.py"], cwd=ROOT)
    assert result.returncode == 0
