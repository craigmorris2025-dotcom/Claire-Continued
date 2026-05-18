from __future__ import annotations

from fastapi.testclient import TestClient


def replay_get(client: TestClient, path: str) -> dict:
    response = client.get(path)
    try:
        body = response.json()
    except Exception:
        body = {"raw_text": response.text}
    return {
        "method": "GET",
        "path": path,
        "status_code": response.status_code,
        "json": body,
        "governance": {
            "read_only": True,
            "mutation_authority": False,
            "runtime_truth_mutation": False,
        },
    }
