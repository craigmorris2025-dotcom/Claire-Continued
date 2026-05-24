from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.proof.post_ui_response_reference import persist_post_ui_response_reference


def main() -> int:
    payload = persist_post_ui_response_reference(output=ROOT / "reports" / "POST_UI_RESPONSE_REFERENCE.json")
    print(
        json.dumps(
            {
                "status": payload.get("status"),
                "file_count": payload.get("file_count"),
                "record_count": payload.get("record_count"),
                "response_classes": payload.get("response_classes"),
                "required_surface_contracts": payload.get("required_surface_contracts"),
                "recovered_route_count": len(payload.get("recovered_routes", [])),
                "paths": payload.get("paths"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload.get("status") == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
