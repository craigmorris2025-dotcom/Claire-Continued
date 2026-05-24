from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime_core.app import create_app


def build_active_endpoint_payload() -> dict[str, object]:
    app = create_app()
    endpoints = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", []) or [])
        if not path or not methods:
            continue
        endpoint = getattr(route, "endpoint", None)
        endpoints.append(
            {
                "path": path,
                "methods": methods,
                "name": getattr(route, "name", ""),
                "module": getattr(endpoint, "__module__", ""),
                "endpoint": getattr(endpoint, "__name__", ""),
            }
        )
    return {
        "schema_version": "claire.active_endpoints.v1",
        "active_app": "main.py -> runtime_core.app:create_app",
        "route_count": len(endpoints),
        "endpoint_count": len(endpoints),
        "endpoints": sorted(endpoints, key=lambda item: (str(item["path"]), str(item["methods"]))),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/backend_baseline_20260524_ACTIVE_ENDPOINTS.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_active_endpoint_payload()
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"route_count": payload["route_count"], "endpoint_count": payload["endpoint_count"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
