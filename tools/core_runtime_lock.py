from __future__ import annotations



import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json

from datetime import datetime, timezone

from pathlib import Path



from fastapi.testclient import TestClient



from runtime_core.app import create_app





TOOL_NAME = "core_runtime_lock"

OUTPUT_FILE = "reports/core_runtime_lock.json"





def _now() -> str:

    return datetime.now(timezone.utc).isoformat()





def _root() -> Path:

    return Path(__file__).resolve().parents[1]





def build_state() -> dict:

    app = create_app()

    client = TestClient(app)

    mounted = {getattr(route, "path", "") for route in app.routes}



    checks = {}

    for path in [

        "/health",

        "/openapi.json",

        "/dashboard/payload/status",

        "/runtime/continuous/status",

        "/api/dashboard/search/provider/status",

        "/api/cockpit/operational-status",

    ]:

        try:

            checks[path] = client.get(path).status_code

        except Exception as exc:

            checks[path] = f"{exc.__class__.__name__}: {exc}"



    required = ["/health", "/openapi.json", "/dashboard/payload/status"]

    missing = [path for path in required if path not in mounted]



    return {

        "tool": TOOL_NAME,

        "status": "success" if not missing else "degraded",

        "created_at": _now(),

        "route_count": len(mounted),

        "missing_required_routes": missing,

        "checks": checks,

        "backend_owns_truth": True,

        "runtime_truth_over_ui_assumptions": True,

    }





def main() -> int:

    root = _root()

    output = root / OUTPUT_FILE

    output.parent.mkdir(parents=True, exist_ok=True)



    try:

        state = build_state()

        output.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

        print(json.dumps(state, indent=2))

        return 0

    except Exception as exc:

        failure = {

            "tool": TOOL_NAME,

            "status": "failed",

            "created_at": _now(),

            "error": f"{exc.__class__.__name__}: {exc}",

        }

        output.write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")

        print(json.dumps(failure, indent=2))

        return 1





if __name__ == "__main__":

    raise SystemExit(main())



