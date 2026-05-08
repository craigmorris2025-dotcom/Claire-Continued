import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_runtime_state_engine_runs():
    result = subprocess.run([sys.executable, "tools/runtime_state_engine.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert (ROOT / "data" / "runtime" / "runtime_state.json").exists()

def test_runtime_state_loader_imports():
    from claire.runtime.runtime_state_engine import load_runtime_state
    state = load_runtime_state(ROOT)
    assert "status" in state
