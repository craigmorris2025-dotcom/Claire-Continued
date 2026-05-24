
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from runtime_core.demo.demo_scenario_registry import load_demo_scenarios

DEMO_RUN_OUTPUT_PATH = Path("data/demo/guided_demo_run.json")

def run_guided_demo(scenario_id: str | None = None) -> Dict[str, Any]:
    registry = load_demo_scenarios()
    scenarios = registry.get("scenarios", [])

    selected = None
    if scenario_id:
        selected = next((s for s in scenarios if s.get("id") == scenario_id), None)
    if selected is None and scenarios:
        selected = scenarios[0]

    if selected is None:
        result = {
            "version": "16.57",
            "status": "blocked",
            "reason": "No demo scenarios available.",
        }
    else:
        result = {
            "version": "16.57",
            "status": "demo_ready",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scenario": selected,
            "guided_steps": [
                "Open Claire.",
                "Select the demo scenario.",
                "Run the governed intelligence flow.",
                "Review thesis, evidence, route, and recommendation.",
                "Open proof artifacts for buyer/operator review.",
            ],
            "success_test": "A non-programmer can understand the demo flow without file-level explanation.",
        }

    DEMO_RUN_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEMO_RUN_OUTPUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
