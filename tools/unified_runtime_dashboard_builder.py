from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    output = root / "data" / "runtime" / "unified_runtime_dashboard.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "dashboard": "unified_runtime_dashboard",
        "status": "success",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
    }

    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
