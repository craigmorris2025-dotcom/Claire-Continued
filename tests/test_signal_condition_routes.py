from fastapi.testclient import TestClient

from main import app


def _breakthrough_signal_payload():
    return {
        "raw_input": "connected_signal_stream",
        "mode": "deterministic",
        "source_mode": "connected_live",
        "sources": {
            "market": {
                "source_type": "live_market",
                "sector": "technology",
                "signals": [
                    "autonomous enterprise workflow platform hidden bottleneck category creation demand accelerating"
                ],
                "metrics": {"growth": 0.95, "volatility": 0.2, "alignment": 0.9},
            },
            "patent": {
                "source_type": "live_patent",
                "sector": "technology",
                "signals": ["novel AI orchestration design patent filings accelerating"],
                "metrics": {"activity": 0.96, "novelty": 0.95},
            },
            "financial": {
                "source_type": "live_financial",
                "sector": "technology",
                "signals": ["strong buyer ROI budget expansion"],
                "metrics": {"health": 0.91, "risk": 0.15},
            },
        },
    }


def test_runtime_signals_activate_breakthrough_design_branch_and_dashboard_truth():
    client = TestClient(app)

    run = client.post("/evaluate", json=_breakthrough_signal_payload()).json()

    assert run["status"] == "success"
    assert run["route_selected"] == "breakthrough_design"
    assert run["core_lifecycle"]["route"] == "breakthrough_design"
    assert run["core_lifecycle"]["completion_gate"]["status"] == "complete"
    assert run["core_lifecycle"]["completion_gate"]["complete_stage_count"] == 30
    assert run["design_portal"]["route_to_design"] is True
    assert run["design_output"]["status"] == "success"
    assert run["source_authority"]["live_evidence_present"] is True

    state = client.get("/api/dashboard/state").json()
    assert state["lifecycle"]["route_selected"] == "breakthrough_design"
