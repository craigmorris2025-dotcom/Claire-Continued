import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_autonomous_install_validator_runs_on_itself():
    target = ROOT / "tools" / "autonomous_install_validator.py"
    result = subprocess.run([sys.executable, "tools/autonomous_install_validator.py", str(target)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode in (0, 1)
    assert (ROOT / "data" / "runtime" / "autonomous_install_validation.json").exists()
