from __future__ import annotations

from fastapi.testclient import TestClient


def test_backend_boundary_delegates_to_canonical_claire_app():
    from backend.app import create_backend_app

    client = TestClient(create_backend_app())

    assert client.get("/health").status_code == 200
    payload = client.get("/dashboard/payload")
    assert payload.status_code == 200
    assert payload.json()["backend_owns_truth"] is True
