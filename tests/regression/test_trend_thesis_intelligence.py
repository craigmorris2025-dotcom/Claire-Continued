import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_trend_thesis_intelligence_runs():
    result = subprocess.run([sys.executable, "tools/trend_thesis_intelligence_upgrade.py"], cwd=ROOT)
    assert result.returncode == 0
    assert (ROOT / "data" / "intelligence" / "trend_thesis_intelligence.json").exists()

def test_trend_thesis_loader_imports():
    from claire.intelligence.trend_thesis_intelligence import load_trend_thesis_intelligence
    payload = load_trend_thesis_intelligence(ROOT)
    assert "readiness" in payload or payload.get("status") == "not_available"
