import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_portfolio_breakthrough_routing_runs():
    result = subprocess.run([sys.executable, "tools/portfolio_breakthrough_routing_upgrade.py"], cwd=ROOT)
    assert result.returncode == 0
    assert (ROOT / "data" / "intelligence" / "portfolio_breakthrough_routing.json").exists()

def test_portfolio_breakthrough_loader_imports():
    from claire.intelligence.portfolio_breakthrough_routing import load_portfolio_breakthrough_routing
    payload = load_portfolio_breakthrough_routing(ROOT)
    assert "route_scores" in payload or payload.get("status") == "not_available"
