import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_runtime_recovery_engine_runs():
    result = subprocess.run([sys.executable, "tools/runtime_recovery_engine.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert (ROOT / "data" / "runtime" / "runtime_recovery_state.json").exists()
