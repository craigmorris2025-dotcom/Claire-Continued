from __future__ import annotations
from fastapi.testclient import TestClient

def replay_get(client: TestClient, path: str) -> dict:
    response = client.get(path)
    try:
        body = response.json()
    except Exception:
        body = None
    return {"status_code": response.status_code, "json": body}
