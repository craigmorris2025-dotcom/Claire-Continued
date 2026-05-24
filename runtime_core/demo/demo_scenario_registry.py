
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DEMO_SCENARIO_PATH = Path("data/demo/demo_scenarios.json")

DEFAULT_DEMO_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "demo_001_governed_opportunity_intelligence",
        "title": "Governed Opportunity Intelligence Pilot",
        "goal": "Detect weak signals, form an opportunity thesis, and produce an evidence-backed go/no-go memo.",
        "domain": "enterprise AI strategy",
        "expected_outputs": [
            "opportunity thesis",
            "evidence packet",
            "source lineage placeholder",
            "portfolio implication",
            "go/no-go recommendation",
        ],
        "operator_time_target_minutes": 10,
        "status": "ready",
    },
    {
        "id": "demo_002_portfolio_breakthrough_routing",
        "title": "Portfolio + Breakthrough Routing Demo",
        "goal": "Show how Claire routes an opportunity toward portfolio action or breakthrough classification.",
        "domain": "market intelligence",
        "expected_outputs": [
            "trend thesis",
            "portfolio recommendation",
            "breakthrough classification",
            "route explanation",
        ],
        "operator_time_target_minutes": 10,
        "status": "ready",
    },
    {
        "id": "demo_003_acquisition_package_preview",
        "title": "Acquisition Package Preview Demo",
        "goal": "Show how Claire can assemble buyer-readable proof and positioning artifacts.",
        "domain": "strategic acquisition readiness",
        "expected_outputs": [
            "category thesis",
            "proof summary",
            "governance summary",
            "buyer fit map placeholder",
        ],
        "operator_time_target_minutes": 10,
        "status": "ready",
    },
]

def seed_demo_scenarios() -> Dict[str, Any]:
    DEMO_SCENARIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "16.56",
        "scenario_count": len(DEFAULT_DEMO_SCENARIOS),
        "scenarios": DEFAULT_DEMO_SCENARIOS,
    }
    DEMO_SCENARIO_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

def load_demo_scenarios() -> Dict[str, Any]:
    if not DEMO_SCENARIO_PATH.exists():
        return seed_demo_scenarios()
    return json.loads(DEMO_SCENARIO_PATH.read_text(encoding="utf-8"))
