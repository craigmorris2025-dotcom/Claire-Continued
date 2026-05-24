from __future__ import annotations
from typing import Any
from fastapi.testclient import TestClient
from runtime_core.api._s43_governance import build_governance

def replay_get(client: TestClient, path: str) -> dict[str, Any]:
    response = client.get(path)
    try:
        payload = response.json()
    except Exception:
        payload = {"raw": response.text}
    return {"path": path, "status_code": response.status_code, "json": payload, "governance": build_governance(), "read_only": True, "replay_ok": response.status_code == 200}

def replay_route_contract(client: TestClient, path: str) -> dict[str, Any]:
    return replay_get(client, path)

def replay_operator_status_contract(client: TestClient) -> dict[str, Any]:
    return replay_get(client, "/operator/runtime/status")
