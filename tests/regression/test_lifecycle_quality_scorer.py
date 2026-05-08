import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_lifecycle_quality_scorer_runs():
    result = subprocess.run([sys.executable, "tools/lifecycle_quality_scorer.py"], cwd=ROOT)
    assert result.returncode == 0
    assert (ROOT / "data" / "intelligence" / "lifecycle_quality_score.json").exists()

def test_lifecycle_quality_loader_imports():
    from claire.intelligence.lifecycle_quality import load_lifecycle_quality_score
    payload = load_lifecycle_quality_score(ROOT)
    assert "score" in payload or payload.get("status") == "not_available"
