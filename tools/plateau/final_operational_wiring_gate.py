from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime_core.app import create_app
from runtime_core.dashboard.final_dashboard_payload import build_final_dashboard_payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _score(ok: bool) -> int:
    return 100 if ok else 0


def run_gate() -> dict[str, Any]:
    app = create_app()
    client = TestClient(app)
    operational = client.get("/api/operational/control-plane").json()
    v5 = build_final_dashboard_payload(routes=app.routes)

    endpoint_checks = {}
    for action in operational.get("actions", []):
        endpoint = action.get("endpoint")
        method = str(action.get("method") or "GET").upper()
        if not endpoint:
            endpoint_checks[endpoint or "unknown"] = {"ok": False, "status_code": None}
            continue
        if method == "POST":
            response = client.post(endpoint, json=action.get("body") or {})
        else:
            response = client.get(endpoint)
        endpoint_checks[endpoint] = {"ok": response.status_code == 200, "status_code": response.status_code}

    checks = {
        "operational_control_plane_ready": operational.get("status") == "operational_ready",
        "required_routes_mounted": operational.get("route_health", {}).get("status") == "ready",
        "required_files_present": operational.get("file_readiness", {}).get("status") == "ready",
        "dashboard_uses_operational_control_plane": "operational_control_plane" in v5,
        "dashboard_has_callable_actions": len(operational.get("actions", [])) >= 8 and all(item["ok"] for item in endpoint_checks.values()),
        "lifecycle_api_operational": client.get("/api/lifecycle/stage-registry").json().get("stage_count") == 30,
        "threshold_api_operational": client.get("/api/lifecycle/threshold-provenance").json().get("threshold_rule_count", 0) > 0,
        "source_lineage_api_operational": client.get("/api/source-lineage/status").json().get("status") == "ready",
        "update_governance_safe_locked": client.get("/api/update/status").json().get("automatic_updates_enabled") is False,
        "internet_authority_safe_locked": operational.get("internet_authority", {}).get("live_internet_enabled") is False,
    }
    scores = {key: _score(value) for key, value in checks.items()}
    completion = min(scores.values()) if scores else 0
    report = {
        "gate": "claire_final_operational_wiring_gate",
        "generated_at": _utc_now(),
        "status": "complete" if completion == 100 else "incomplete",
        "completion_percent": completion,
        "scores": scores,
        "checks": checks,
        "endpoint_checks": endpoint_checks,
        "operational_summary": {
            "status": operational.get("status"),
            "completion_percent": operational.get("completion_percent"),
            "route_health": operational.get("route_health", {}).get("status"),
            "file_readiness": operational.get("file_readiness", {}).get("status"),
            "source_lineage": operational.get("source_lineage", {}).get("status"),
            "update_governance": operational.get("update_governance", {}).get("status"),
            "internet_authority": operational.get("internet_authority", {}).get("status"),
        },
    }
    path = ROOT / "reports" / "final_operational_wiring_gate.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    report = run_gate()
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
