from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from claire.app import create_app


REQUIRED_ROUTES = [
    "/health",
    "/docs",
    "/openapi.json",
    "/dashboard/payload",
    "/dashboard/payload/status",
    "/runtime/continuous/status",
    "/api/dashboard/search/provider/status",
    "/api/dashboard/search/provider/probe",
    "/api/dashboard/search/live",
    "/api/dashboard/search/smoke/google",
    "/api/cockpit/operational-status",
    "/api/feeds/live-source-catalog/status",
    "/api/feeds/live-source-catalog/health",
]

REQUIRED_PAYLOAD_KEYS = [
    "backend_owns_truth",
    "lifecycle",
    "end_state_alignment",
    "system_identity",
    "operating_model",
    "route_policy",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _write_report(payload: dict) -> None:
    path = _root() / "reports" / "active_runtime_check.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    try:
        app = create_app()
        mounted = {getattr(route, "path", "") for route in app.routes}
        missing = [route for route in REQUIRED_ROUTES if route not in mounted]

        client = TestClient(app)
        health_code = client.get("/health").status_code
        openapi_code = client.get("/openapi.json").status_code
        payload_response = client.get("/dashboard/payload")
        payload_status_code = client.get("/dashboard/payload/status").status_code
        payload = payload_response.json() if payload_response.status_code == 200 else {}
        missing_payload_keys = [key for key in REQUIRED_PAYLOAD_KEYS if key not in payload]

        end_state = payload.get("end_state_alignment", {}) if isinstance(payload, dict) else {}
        route_policy = end_state.get("route_policy", {}) if isinstance(end_state, dict) else {}
        end_state_aligned = (
            payload.get("backend_owns_truth") is True
            and not missing_payload_keys
            and route_policy.get("breakthrough_is_default") is False
            and route_policy.get("portfolio_is_normal_early_path") is True
        )

        status = "success" if (
            not missing
            and not missing_payload_keys
            and health_code == 200
            and openapi_code == 200
            and end_state_aligned
        ) else "degraded"

        _write_report({
            "check": "active_runtime_check",
            "status": status,
            "created_at": _now(),
            "missing_routes": missing,
            "missing_payload_keys": missing_payload_keys,
            "end_state_aligned": end_state_aligned,
            "route_count": len(mounted),
            "health_code": health_code,
            "openapi_code": openapi_code,
            "dashboard_payload_code": payload_response.status_code,
            "dashboard_payload_status_code": payload_status_code,
            "truth": "completed proof adapter; degraded state is reported in JSON, not as process crash",
        })
        return 0
    except Exception as exc:
        _write_report({
            "check": "active_runtime_check",
            "status": "failed",
            "created_at": _now(),
            "error": f"{exc.__class__.__name__}: {exc}",
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
