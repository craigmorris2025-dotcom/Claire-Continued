from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.proof.verified_output_proof import persist_verified_output_proof_binder


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    return fallback


def main() -> int:
    run_spine = read_json(ROOT / "data" / "continuous_runtime" / "current_run.json", {})
    if not isinstance(run_spine, dict) or not run_spine.get("run_id"):
        print(json.dumps({"status": "missing_current_run"}, indent=2))
        return 1
    binder = persist_verified_output_proof_binder(run_spine, project_root=ROOT)
    print(
        json.dumps(
            {
                "status": binder.get("status"),
                "run_id": binder.get("run_id"),
                "completion_percent": binder.get("completion_percent"),
                "proof_phase_complete": binder.get("proof_phase_complete"),
                "area_scores": binder.get("area_scores"),
                "portfolio_status": binder.get("portfolio_route_proof", {}).get("status"),
                "technology_status": binder.get("technology_route_proof", {}).get("status"),
                "paths": binder.get("paths"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
