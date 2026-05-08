import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_runtime_intelligence_layer_runs():
    result = subprocess.run([sys.executable, "tools/runtime_intelligence_layer.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert (ROOT / "data" / "runtime" / "runtime_intelligence.json").exists()

def test_runtime_intelligence_loader_imports():
    from claire.runtime.runtime_intelligence import load_runtime_intelligence
    payload = load_runtime_intelligence(ROOT)
    assert "status" in payload
