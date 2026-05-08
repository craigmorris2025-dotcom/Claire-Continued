"""
Small smoke-runner for Claire lifecycle regression fixtures.

Usage from project root:

    python tests/regression/run_lifecycle_smoke.py

This script is useful when pytest is not installed. It exits non-zero if the
lifecycle is not fully active for every fixture.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Let this file run from project root without package install.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from claire.domain.contract import ContractValidator
from claire.orchestrator.pipeline_v4 import PipelineOrchestrator
from tests.regression.fixtures.lifecycle_inputs import ALL_FIXTURES


def main() -> int:
    orchestrator = PipelineOrchestrator()
    validator = ContractValidator()
    failures = []

    for name, payload in ALL_FIXTURES.items():
        result = orchestrator.execute(validator.validate_intent(payload)).to_dict()
        summary = result.get("lifecycle_summary", {})
        line = {
            "fixture": name,
            "status": result.get("status"),
            "implemented": summary.get("implemented_stage_count"),
            "active": summary.get("active_stage_count"),
            "partial": summary.get("partial_stage_count"),
            "pending": summary.get("pending_stage_count"),
            "decision": result.get("decision_classification"),
            "sector": result.get("market_gap", {}).get("sector"),
        }
        print(json.dumps(line, indent=2))

        if line["status"] != "success" or line["implemented"] != 21 or line["active"] != 21 or line["partial"] != 0 or line["pending"] != 0:
            failures.append(line)

    if failures:
        print("\nLifecycle regression failures:")
        print(json.dumps(failures, indent=2))
        return 1

    print("\nLifecycle regression smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
