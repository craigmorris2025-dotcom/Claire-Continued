import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_runtime_manifest_builder_runs():
    result = subprocess.run([sys.executable, "tools/runtime_manifest_builder.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert (ROOT / "data" / "runtime" / "runtime_manifest.json").exists()

def test_active_module_registry_runs():
    result = subprocess.run([sys.executable, "tools/active_module_registry.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    data = json.loads((ROOT / "data" / "runtime" / "active_module_registry.json").read_text(encoding="utf-8"))
    assert data["failed_count"] == 0

def test_dependency_map_runs():
    result = subprocess.run([sys.executable, "tools/runtime_dependency_map.py"], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert (ROOT / "data" / "runtime" / "runtime_dependency_map.json").exists()
