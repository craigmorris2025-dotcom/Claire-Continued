import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_master_control_layer_builder_runs():
    result = subprocess.run(
        [sys.executable, "tools/master_control_layer_builder.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0

    assert (
        ROOT / "data" / "runtime" / "master_control_state.json"
    ).exists()


def test_master_control_loader_imports():
    from claire.control.master_control_state import (
        load_master_control_state,
    )

    payload = load_master_control_state(ROOT)

    assert (
        "runtime" in payload
        or payload.get("status") == "not_available"
    )
