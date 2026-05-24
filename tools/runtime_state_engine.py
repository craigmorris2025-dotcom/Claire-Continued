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





def _now() -> str:

    return datetime.now(timezone.utc).isoformat()





def _root() -> Path:

    return Path(__file__).resolve().parents[1]





def build_runtime_state(root: Path | None = None) -> dict:

    root = root or _root()

    app = create_app()

    mounted = {getattr(route, "path", "") for route in app.routes}

    client = TestClient(app)



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



    missing_core = [

        path for path in ["/health", "/openapi.json", "/dashboard/payload/status"]

        if path not in mounted

    ]



    return {

        "engine": "runtime_state_engine",

        "status": "success" if not missing_core else "degraded",

        "created_at": _now(),

        "route_count": len(mounted),

        "missing_core_routes": missing_core,

        "checks": checks,

        "backend_owns_truth": True,

        "cockpit_presentation_only": True,

        "runtime_truth_over_ui_assumptions": True,

    }





def write_runtime_state(root: Path | None = None) -> dict:

    root = root or _root()

    state = build_runtime_state(root)

    path = root / "data" / "runtime" / "runtime_state.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(state, indent=2))

    print(f"Runtime state written: {path}")

    return state





def main() -> int:

    try:

        write_runtime_state()

        return 0

    except Exception as exc:

        root = _root()

        path = root / "data" / "runtime" / "runtime_state.json"

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(json.dumps({

            "engine": "runtime_state_engine",

            "status": "failed",

            "created_at": _now(),

            "error": f"{exc.__class__.__name__}: {exc}",

        }, indent=2) + "\n", encoding="utf-8")

        return 1





if __name__ == "__main__":

    raise SystemExit(main())



